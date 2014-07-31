import json
import logging
import uuid

from analyticsclient.client import Client
from analyticsclient.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.db import connection, DatabaseError
from django.http import HttpResponse, Http404
from django.views.generic import View, TemplateView


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

        username = password = uuid.uuid4().hex[0:30]
        User.objects.create_user(username, password=password)
        user = authenticate(username=username, password=password)
        login(request, user)

        return HttpResponse()


class AuthError(TemplateView):
    template_name = 'auth_error.html'
