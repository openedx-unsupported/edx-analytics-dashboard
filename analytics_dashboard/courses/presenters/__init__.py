import datetime
import logging

from django.conf import settings
from analyticsclient.client import Client


logger = logging.getLogger(__name__)


class BasePresenter(object):
    """
    This is the base class for the pages and sets up the analytics client
    for the presenters to use to access the data API.
    """

    def __init__(self, course_id, timeout=5):
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)
        self.course_id = course_id
        self.course = self.client.courses(self.course_id)

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
