import json
import logging
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.views import LogoutView, logout_then_login
from django.db import connection, DatabaseError
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.core.urlresolvers import reverse_lazy

from analytics_dashboard.courses import permissions
try:
    import newrelic.agent
except ImportError:  # pragma: no cover
    newrelic = None  # pylint: disable=invalid-name

logger = logging.getLogger(__name__)
User = get_user_model()

# Health constants
OK = u'OK'
UNAVAILABLE = u'UNAVAILABLE'


def status(_request):
    return HttpResponse()


def health(_request):
    if newrelic:  # pragma: no cover
        newrelic.agent.ignore_transaction()
    overall_status = database_status = UNAVAILABLE

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        database_status = OK
    except DatabaseError as e:
        logger.exception('Insights database is not reachable: %s', e)
        database_status = UNAVAILABLE

    overall_status = OK if (database_status == OK) else UNAVAILABLE

    data = {
        'overall_status': overall_status,
        'detailed_status': {
            'database_connection': database_status,
        }
    }

    return HttpResponse(json.dumps(data), content_type='application/json', status=200 if overall_status == OK else 503)


class AutoAuth(View):
    """
    Creates and authenticates a new User.

    If the setting ENABLE_AUTO_AUTH is not set to True, returns a 404.
    """

    def get(self, request, *_args, **_kwargs):
        if not settings.ENABLE_AUTO_AUTH:
            raise Http404

        if not settings.AUTO_AUTH_USERNAME_PREFIX:
            raise ValueError('AUTO_AUTH_USERNAME_PREFIX must be set!')

        # Create a new user
        username = password = settings.AUTO_AUTH_USERNAME_PREFIX + uuid.uuid4().hex[0:20]
        user = User.objects.create_user(username, password=password)

        # Grant user access to demo course
        permissions.set_user_course_permissions(user, ['edX/DemoX/Demo_Course'])

        # Login the new user
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('/')


class InsightsLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        """
        Revoke user permissions and logout
        """
        # Revoke permissions
        permissions.revoke_user_course_permissions(request.user)

        # Back to the standard logout flow
        return super(InsightsLogoutView, self).dispatch(request, *args, **kwargs)


def insights_logout_then_login(request, login_url=reverse_lazy('login')):
    """
    Logout then login
    """
    permissions.revoke_user_course_permissions(request.user)
    return logout_then_login(request, login_url=login_url)


class ServiceUnavailableView(TemplateView):
    """
    Service unavailable error page requesting users to wait and reload the page.
    """
    template_name = "503.html"


class LandingView(TemplateView):
    """
    Displays a public landing page when users first come to the site.
    """
    template_name = "core/landing.html"

    def dispatch(self, request, *args, **kwargs):
        """ Non logged in users will be directed to the landing page. """
        if request.user.is_anonymous():
            return super(LandingView, self).dispatch(request, *args, **kwargs)
        return redirect('courses:index')

    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)
        context['research_url'] = settings.RESEARCH_URL
        context['open_source_url'] = settings.OPEN_SOURCE_URL
        context['show_research'] = settings.SHOW_LANDING_RESEARCH and settings.RESEARCH_URL
        audience_message_column_width = 6
        if context['show_research']:
            audience_message_column_width = 4
        context['audience_message_column_width'] = audience_message_column_width

        return context
