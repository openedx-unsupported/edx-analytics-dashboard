import datetime
from bok_choy.web_app_test import WebAppTest
from bok_choy.promise import EmptyPromise

from analyticsclient import demographic

from acceptance_tests import AnalyticsApiClientMixin, FooterMixin
from acceptance_tests.pages import CourseEnrollmentActivityPage, CourseEnrollmentGeographyPage


class CourseEnrollmentTests(AnalyticsApiClientMixin, FooterMixin):
    """
    Tests for the Enrollment page.
    """

    DASHBOARD_DATE_FORMAT = '%B %d, %Y'
    page = None

    def setUp(self):
        super(CourseEnrollmentTests, self).setUp()
        self.api_date_format = self.api_client.DATE_FORMAT

    def assertValidHref(self, selector):
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertNotEqual(element.attrs('href')[0], '#')

    def assertTableColumnHeadingsEqual(self, table_selector, headings):
        rows = self.page.q(css=('%s thead th' % table_selector))
        self.assertTrue(rows.present)
        self.assertListEqual(rows.text, headings)

    def assertElementHasContent(self, css):
        element = self.page.q(css=css)
        self.assertTrue(element.present)
        graph_html = element.html[0]
        self.assertIsNotNone(graph_html)
        self.assertNotEqual(graph_html, '')

    def test_page_exists(self):
        self.page.visit()


class CourseEnrollmentActivityTests(CourseEnrollmentTests, WebAppTest):
    def setUp(self):
        super(CourseEnrollmentActivityTests, self).setUp()
        self.page = CourseEnrollmentActivityPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def assertSummaryPointValueEquals(self, stat_type, value):
        element = self.page.q(css="[data-stat-type=%s] .summary-point-number" % stat_type)
        self.assertTrue(element.present)
        self.assertEqual(int(element.text[0]), value)

    def get_enrollment_data(self):
        """
        Returns enrollment data for 60 days prior to (and including) the most-recent enrollment count collection.
        """

        current_enrollment = self.course.enrollment()[0]
        last_updated = datetime.datetime.strptime(current_enrollment['date'], self.api_date_format)
        start_date = (last_updated - datetime.timedelta(days=60)).strftime(self.api_date_format)
        end_date = (last_updated + datetime.timedelta(days=1)).strftime(self.api_date_format)
        return self.course.enrollment(start_date=start_date, end_date=end_date)

    def test_enrollment_summary_and_graph(self):
        self.page.visit()
        enrollment_data = self.get_enrollment_data()
        current_enrollment = enrollment_data[-1]

        # Check last updated
        last_updated = datetime.datetime.strptime(current_enrollment['date'], self.api_date_format)
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

        # Verify *something* rendered where the graph should be. We cannot easily verify what rendered
        self.assertElementHasContent("[data-section=enrollment-basics] #enrollment-trend-view")

    def test_enrollment_trend_table(self):
        self.page.visit()
        enrollment_data = sorted(self.get_enrollment_data(), reverse=True, key=lambda item: item['date'])

        table_selector = 'div[data-role=enrollment-table] table'
        self.assertTableColumnHeadingsEqual(table_selector, ['Date', 'Count'])

        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = enrollment_data[i]
            expected = [enrollment['date'], enrollment['count']]
            actual = [columns[0].text, int(columns[1].text)]
            self.assertListEqual(actual, expected)

        # Verify CSV button has an href attribute
        selector = "a[data-role=enrollment-trend-csv]"
        self.assertValidHref(selector)


class CourseEnrollmentGeographyTests(CourseEnrollmentTests, WebAppTest):
    def setUp(self):
        super(CourseEnrollmentGeographyTests, self).setUp()
        self.page = CourseEnrollmentGeographyPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def test_enrollment_country_map(self):
        self.page.visit()

        map_selector = "div[data-view=world-map]"

        # ensure that the map data has been loaded (via ajax); otherwise this
        # will timeout
        EmptyPromise(
            lambda: 'Loading Map...' not in self.page.q(css=map_selector + ' p').text,
            "Map finished loading"
        ).fulfill()

        # make sure the map section is present
        element = self.page.q(css=map_selector)
        self.assertTrue(element.present)

        # make sure that the map is present
        element = self.page.q(css=map_selector + " svg[class=datamap]")
        self.assertTrue(element.present)

        # make sure the legend is present
        element = self.page.q(css=map_selector + " svg[class=datamaps-legend]")
        self.assertTrue(element.present)

    def test_enrollment_country_table(self):
        self.page.visit()

        table_section_selector = "div[data-role=enrollment-location-table]"

        # ensure that the map data has been loaded (via ajax); otherwise this
        # will timeout
        EmptyPromise(
            lambda: 'Loading Table...' not in self.page.q(css=table_section_selector + ' p').text,
            "Table finished loading"
        ).fulfill()

        # make sure the map section is present
        element = self.page.q(css=table_section_selector)
        self.assertTrue(element.present)

        # make sure the table is present
        table_selector = table_section_selector + " table"
        element = self.page.q(css=table_selector)
        self.assertTrue(element.present)

        # check the headings
        self.assertTableColumnHeadingsEqual(table_selector, ['Country', 'Count'])

        # Verify CSV button has an href attribute
        selector = "a[data-role=enrollment-location-csv]"
        self.assertValidHref(selector)

        # Check last updated
        enrollment_data = sorted(self.course.enrollment(demographic.LOCATION),
                                 key=lambda item: item['count'], reverse=True)
        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        last_updated = datetime.datetime.strptime(enrollment_data[0]['date'], self.api_date_format)
        element = self.page.q(css="span[data-view=enrollment-by-country-update-date]")
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], last_updated.strftime(self.DASHBOARD_DATE_FORMAT))

        # check the results of the table
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = enrollment_data[i]
            expected = [enrollment['country']['name'], enrollment['count']]
            actual = [columns[0].text, int(columns[1].text)]
            self.assertListEqual(actual, expected)
