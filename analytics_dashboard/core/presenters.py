from django.conf import settings
import datetime

from analyticsclient.client import Client

class BasePresenter(object):

    def __init__(self, timeout=settings.ANALYTICS_API_DEFAULT_TIMEOUT):
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)

    def get_current_date(self):
        return datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)

    @staticmethod
    def parse_api_date(s):
        """ Parse a string according to the API date format. """
        return datetime.datetime.strptime(s, Client.DATE_FORMAT).date()

    @staticmethod
    def parse_api_datetime(s):
        """ Parse a string according to the API datetime format. """
        return datetime.datetime.strptime(s, Client.DATETIME_FORMAT)

    @staticmethod
    def strip_time(s):
        return s[:-7]

    @staticmethod
    def sum_counts(data):
        return sum(datum['count'] for datum in data)
