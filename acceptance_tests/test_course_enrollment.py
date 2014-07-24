from bok_choy.web_app_test import WebAppTest
import datetime
from acceptance_tests import AnalyticsApiClientMixin

from acceptance_tests.pages import CourseEnrollmentPage


class CourseEnrollmentTests(AnalyticsApiClientMixin, WebAppTest):
    """
    Tests for the Enrollment page.
    """

    API_DATE_FORMAT = '%Y-%m-%d'
    DASHBOARD_DATE_FORMAT = '%B %d, %Y'

    def setUp(self):
        super(CourseEnrollmentTests, self).setUp()

        self.page = CourseEnrollmentPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def test_page_exists(self):
        self.page.visit()

    def assertSummaryPointValueEquals(self, stat_type, value):
        element = self.page.q(css="[data-stat-type=%s] .summary-point-number" % stat_type)
        self.assertTrue(element.present)
        self.assertEqual(int(element.text[0]), value)

    def test_enrollment_summary(self):
        self.page.visit()
        current_enrollment = self.course.enrollment()[0]

        # Check last updated
        last_updated = datetime.datetime.strptime(current_enrollment['date'], self.API_DATE_FORMAT)
        element = self.page.q(css="span[data-role=enrollment-last-updated]")
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], last_updated.strftime(self.DASHBOARD_DATE_FORMAT))

        # Check values of summary boxes
        current_enrollment_count = current_enrollment['count']
        self.assertSummaryPointValueEquals('current_enrollment', current_enrollment_count)

        start_date = (last_updated - datetime.timedelta(days=60)).strftime(self.API_DATE_FORMAT)
        end_date = (last_updated + datetime.timedelta(days=1)).strftime(self.API_DATE_FORMAT)
        enrollment_data = self.course.enrollment(start_date=start_date, end_date=end_date)
        for i in [1, 7, 30]:
            stat_type = 'enrollment_change_last_%s_days' % i
            value = current_enrollment_count - enrollment_data[-(i + 1)]['count']
            self.assertSummaryPointValueEquals(stat_type, value)

        # Verify *something* rendered. We cannot easily verify what rendered
        element = self.page.q(css="[data-section=enrollment-basics] #enrollment-trend-view")
        self.assertTrue(element.present)
        graph_html = element.html[0]
        self.assertIsNotNone(graph_html)
        self.assertNotEqual(graph_html, '')
