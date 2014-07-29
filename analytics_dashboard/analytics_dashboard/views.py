import json
import logging
from analyticsclient.client import Client
from analyticsclient.exceptions import ClientError
from django.conf import settings
from django.db import connection, DatabaseError
from django.http import HttpResponse

logger = logging.getLogger(__name__)


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
    except DatabaseError:   # pylint: disable=catching-non-exception
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
