from __future__ import absolute_import

from acceptance_tests.mixins import AnalyticsApiClientMixin, LoginMixin


class CoursePageTestsMixin(LoginMixin, AnalyticsApiClientMixin):
    """ Mixin for course page tests. """

    DASHBOARD_DATE_FORMAT = '%B %d, %Y'
    page = None

    def setUp(self):
        super(CoursePageTestsMixin, self).setUp()
        self.api_date_format = self.analytics_api_client.DATE_FORMAT
        self.api_datetime_format = self.analytics_api_client.DATETIME_FORMAT
