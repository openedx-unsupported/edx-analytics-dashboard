import datetime
from bok_choy.web_app_test import WebAppTest
from bok_choy.promise import EmptyPromise

from analyticsclient import demographic

from acceptance_tests import AnalyticsApiClientMixin, CoursePageTestsMixin, FooterMixin
from acceptance_tests.pages import CourseEnrollmentActivityPage, CourseEnrollmentGeographyPage

_multiprocess_can_split_ = True


class CourseEnrollmentTests(AnalyticsApiClientMixin, FooterMixin, CoursePageTestsMixin):
    """
    Tests for the Enrollment page.
    """

    DASHBOARD_DATE_FORMAT = '%B %d, %Y'
    page = None

    def setUp(self):
        super(CourseEnrollmentTests, self).setUp()
        self.api_date_format = self.api_client.DATE_FORMAT

    def test_page_exists(self):
        self.page.visit()


class CourseEnrollmentActivityTests(CourseEnrollmentTests, WebAppTest):
    def setUp(self):
        super(CourseEnrollmentActivityTests, self).setUp()
        self.page = CourseEnrollmentActivityPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

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
        data_selector = 'data-stat-type=current_enrollment'
        self.assertSummaryPointValueEquals(data_selector, unicode(current_enrollment_count))
        self.assertSummaryTooltipEquals(data_selector, 'Students enrolled in course.')

        # Check value of summary box for last week
        i = 7
        value = current_enrollment_count - enrollment_data[-(i + 1)]['count']
        data_selector = 'data-stat-type=enrollment_change_last_%s_days' % i
        self.assertSummaryPointValueEquals(data_selector, unicode(value))
        self.assertSummaryTooltipEquals(data_selector, 'Change in enrollment during the last 7 days (through 23:59 UTC).')

        # Verify *something* rendered where the graph should be. We cannot easily verify what rendered
        self.assertElementHasContent("[data-section=enrollment-basics] #enrollment-trend-view")

    def test_enrollment_trend_table(self):
        self.page.visit()
        enrollment_data = sorted(self.get_enrollment_data(), reverse=True, key=lambda item: item['date'])

        table_selector = 'div[data-role=enrollment-table] table'
        self.assertTableColumnHeadingsEqual(table_selector, ['Date', 'Total Enrollment'])

        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = enrollment_data[i]
            expected_date = datetime.datetime.strptime(enrollment['date'], self.api_date_format).strftime(
                "%B %d, %Y").replace(' 0', ' ')
            expected = [expected_date, enrollment['count']]
            actual = [columns[0].text, int(columns[1].text)]
            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[1].get_attribute('class'))

        # Verify CSV button has an href attribute
        selector = "a[data-role=enrollment-trend-csv]"
        self.assertValidHref(selector)


class CourseEnrollmentGeographyTests(CourseEnrollmentTests, WebAppTest):
    def setUp(self):
        super(CourseEnrollmentGeographyTests, self).setUp()
        self.page = CourseEnrollmentGeographyPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)
        self.enrollment_data = sorted(self.course.enrollment(demographic.LOCATION),
                                      key=lambda item: item['count'], reverse=True)

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
        self.assertTableColumnHeadingsEqual(table_selector, ['Country', 'Percent', 'Total Enrollment'])

        # Verify CSV button has an href attribute
        selector = "a[data-role=enrollment-location-csv]"
        self.assertValidHref(selector)

        # Check last updated
        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        last_updated = datetime.datetime.strptime(self.enrollment_data[0]['date'], self.api_date_format)
        element = self.page.q(css="span[data-view=enrollment-by-country-update-date]")
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], last_updated.strftime(self.DASHBOARD_DATE_FORMAT))

        # check the results of the table
        self.assertGreater(len(rows), 0)

        sum_count = float(sum([datum['count'] for datum in self.enrollment_data]))

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = self.enrollment_data[i]
            expected_percent = enrollment['count'] / sum_count * 100
            expected_percent_display = '{:.1f}%'.format(expected_percent) if expected_percent >= 0.01 else '< 1%'
            expected = [enrollment['country']['name'], expected_percent_display, enrollment['count']]
            actual = [columns[0].text, columns[1].text, int(columns[2].text)]
            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[1].get_attribute('class'))

    def test_metrics(self):
        self.page.visit()

        enrollment_data = [datum for datum in self.enrollment_data if datum['country']['name'] != 'UNKNOWN']
        self.assertSummaryPointValueEquals('data-stat-type=num-countries', unicode(len(enrollment_data)))

        for i in range(0, 3):
            country = enrollment_data[i]['country']['name']
            self.assertSummaryPointValueEquals('data-stat-type=top-country-{0}'.format((i + 1)), country)
