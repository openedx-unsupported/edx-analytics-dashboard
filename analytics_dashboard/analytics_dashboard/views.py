import json
import logging
import uuid

from analyticsclient.client import Client
from analyticsclient.exceptions import ClientError
import django
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate, REDIRECT_FIELD_NAME
from django.db import connection, DatabaseError
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic import View, TemplateView

from courses import permissions


logger = logging.getLogger(__name__)
User = get_user_model()


def status(_request):
    return HttpResponse()


def health(_request):
    OK = 'OK'
    UNAVAILABLE = 'UNAVAILABLE'

    overall_status = analytics_api_status = database_status = UNAVAILABLE

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        database_status = OK
    except DatabaseError:  # pylint: disable=catching-non-exception
        database_status = UNAVAILABLE

    try:
        client = Client(base_url=settings.DATA_API_URL, auth_token=settings.DATA_API_AUTH_TOKEN)
        if client.status.healthy:
            analytics_api_status = OK
    except ClientError as e:
        logger.exception('API is not reachable from dashboard: %s', e)
        analytics_api_status = UNAVAILABLE

    overall_status = OK if (analytics_api_status == database_status == OK) else UNAVAILABLE

    data = {
        'overall_status': overall_status,
        'detailed_status': {
            'database_connection': database_status,
            'analytics_api': analytics_api_status
        }
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


class AutoAuth(View):
    """
    Creates and authenticates a new User.

    If the setting ENABLE_AUTO_AUTH is not set to True, returns a 404.
    """

    def get(self, request, *_args, **_kwargs):
        if not settings.ENABLE_AUTO_AUTH:
            raise Http404

        # Create a new user
        username = password = 'AUTO_AUTH_' + uuid.uuid4().hex[0:20]
        user = User.objects.create_user(username, password=password)

        # Grant user access to demo course
        permissions.set_user_course_permissions(user, ['edX/DemoX/Demo_Course'])

        # Login the new user
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('/')


class AuthError(TemplateView):
    template_name = 'auth_error.html'


def logout(request, next_page=None, template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME, current_app=None, extra_context=None):
    """
    Revoke user permissions and logout
    """

    # Revoke permissions
    permissions.revoke_user_course_permissions(request.user)

    # Back to the standard logout flow
    return django.contrib.auth.views.logout(request, next_page, template_name, redirect_field_name, current_app,
                                            extra_context)
