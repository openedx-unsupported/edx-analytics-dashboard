import os
from analyticsclient.client import Client

DASHBOARD_SERVER_URL = os.environ.get('DASHBOARD_SERVER_URL', 'http://127.0.0.1:8000')


class AnalyticsApiClientMixin(object):
    def setUp(self):
        super(AnalyticsApiClientMixin, self).setUp()

        api_url = os.environ.get('API_SERVER_URL', 'http://127.0.0.1:8001/api/v0')
        auth_token = os.environ.get('API_AUTH_TOKEN', 'analytics')
        self.api_client = Client(api_url, auth_token=auth_token)
