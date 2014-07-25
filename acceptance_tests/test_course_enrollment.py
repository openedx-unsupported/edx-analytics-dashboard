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

    def get_enrollment_data(self):
        """
        Returns enrollment data for 60 days prior to (and including) the most-recent enrollment count collection.
        """

        current_enrollment = self.course.enrollment()[0]
        last_updated = datetime.datetime.strptime(current_enrollment['date'], self.API_DATE_FORMAT)
        start_date = (last_updated - datetime.timedelta(days=60)).strftime(self.API_DATE_FORMAT)
        end_date = (last_updated + datetime.timedelta(days=1)).strftime(self.API_DATE_FORMAT)
        return self.course.enrollment(start_date=start_date, end_date=end_date)

    def test_enrollment_summary(self):
        self.page.visit()
        enrollment_data = self.get_enrollment_data()
        current_enrollment = enrollment_data[-1]

        # Check last updated
        last_updated = datetime.datetime.strptime(current_enrollment['date'], self.API_DATE_FORMAT)
        element = self.page.q(css="span[data-role=enrollment-last-updated]")
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], last_updated.strftime(self.DASHBOARD_DATE_FORMAT))

        # Check values of summary boxes
        current_enrollment_count = current_enrollment['count']
        self.assertSummaryPointValueEquals('current_enrollment', current_enrollment_count)

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

    def test_enrollment_table(self):
        self.page.visit()
        enrollment_data = sorted(self.get_enrollment_data(), reverse=True, key=lambda item: item['date'])

        rows = self.page.q(css='div[data-role=enrollment-table] table thead th')
        self.assertTrue(rows.present)
        self.assertListEqual(rows.text, ['Date', 'Count'])

        rows = self.page.browser.find_elements_by_css_selector('div[data-role=enrollment-table] table tbody tr')
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = enrollment_data[i]
            expected = [enrollment['date'], enrollment['count']]
            actual = [columns[0].text, int(columns[1].text)]
            self.assertListEqual(actual, expected)
