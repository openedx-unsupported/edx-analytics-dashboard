import datetime

from bok_choy.web_app_test import WebAppTest
from analyticsclient.constants import demographic, UNKNOWN_COUNTRY_CODE

from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CourseEnrollmentActivityPage, CourseEnrollmentGeographyPage


_multiprocess_can_split_ = True


class CourseEnrollmentActivityTests(CoursePageTestsMixin, WebAppTest):
    def setUp(self):
        super(CourseEnrollmentActivityTests, self).setUp()
        self.page = CourseEnrollmentActivityPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def get_enrollment_data(self):
        """
        Returns all historical enrollment data for enrollment count collection.
        """
        end_date = datetime.datetime.utcnow()
        end_date_string = end_date.strftime(self.api_client.DATE_FORMAT)
        return self.course.enrollment(start_date=None, end_date=end_date_string)

    def test_page(self):
        super(CourseEnrollmentActivityTests, self).test_page()
        self._test_enrollment_metrics_and_graph()
        self._test_enrollment_trend_table()

    def _get_data_update_message(self):
        current_enrollment = self.course.enrollment()[0]
        last_updated = datetime.datetime.strptime(current_enrollment['created'], self.api_datetime_format)
        return 'Enrollment activity data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)

    def _test_enrollment_metrics_and_graph(self):
        """ Verify the graph loads and that the metric tiles display the correct information. """

        enrollment_data = self.get_enrollment_data()
        current_enrollment = enrollment_data[-1]

        # Check values of summary boxes
        current_enrollment_count = current_enrollment['count']
        data_selector = 'data-stat-type=current_enrollment'
        self.assertSummaryPointValueEquals(data_selector, self.format_number(current_enrollment_count))
        self.assertSummaryTooltipEquals(data_selector, u'Students enrolled in the course.')

        # Check value of summary box for last week
        i = 7
        value = current_enrollment_count - enrollment_data[-(i + 1)]['count']
        data_selector = 'data-stat-type=enrollment_change_last_%s_days' % i
        self.assertSummaryPointValueEquals(data_selector, unicode(value))
        self.assertSummaryTooltipEquals(data_selector,
                                        u'The difference between the number of students enrolled at the end of the day yesterday and one week before.')

        # Verify *something* rendered where the graph should be. We cannot easily verify what rendered
        self.assertElementHasContent("[data-section=enrollment-basics] #enrollment-trend-view")

    def _test_enrollment_trend_table(self):
        """ Verify the information rendered in the table is correct. """

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
            expected = [expected_date, self.format_number(enrollment['count'])]
            actual = [columns[0].text, columns[1].text]
            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[1].get_attribute('class'))

        # Verify CSV button has an href attribute
        selector = "a[data-role=enrollment-trend-csv]"
        self.assertValidHref(selector)


class CourseEnrollmentGeographyTests(CoursePageTestsMixin, WebAppTest):
    def setUp(self):
        super(CourseEnrollmentGeographyTests, self).setUp()
        self.page = CourseEnrollmentGeographyPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)
        self.enrollment_data = sorted(self.course.enrollment(demographic.LOCATION),
                                      key=lambda item: item['count'], reverse=True)

    def test_page(self):
        super(CourseEnrollmentGeographyTests, self).test_page()
        self._test_enrollment_country_map()
        self._test_enrollment_country_table()
        self._test_metrics()

    def _get_data_update_message(self):
        current_enrollment = self.course.enrollment(demographic.LOCATION)[0]
        last_updated = datetime.datetime.strptime(current_enrollment['created'], self.api_datetime_format)
        return 'Geographic student data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)

    def _test_enrollment_country_map(self):
        """ Verify the geolocation map is loaded. """

        map_selector = "div[data-view=world-map]"

        # Ensure the map is loaded via AJAX
        self.fulfill_loading_promise(map_selector)

        # make sure the map section is present
        element = self.page.q(css=map_selector)
        self.assertTrue(element.present)

        # make sure that the map is present
        element = self.page.q(css=map_selector + " svg[class=datamap]")
        self.assertTrue(element.present)

        # make sure the legend is present
        element = self.page.q(css=map_selector + " svg[class=datamaps-legend]")
        self.assertTrue(element.present)

    def _test_enrollment_country_table(self):
        """ Verify the geolocation enrollment table is loaded. """

        table_section_selector = "div[data-role=enrollment-location-table]"

        # Ensure the table is loaded via AJAX
        self.fulfill_loading_promise(table_section_selector)

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

        # Check the results of the table
        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        sum_count = float(sum([datum['count'] for datum in self.enrollment_data]))

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = self.enrollment_data[i]
            expected_percent = enrollment['count'] / sum_count * 100
            expected_percent_display = '{:.1f}%'.format(expected_percent) if expected_percent >= 1.0 else '< 1%'

            country_name = enrollment['country']['name']
            if country_name == UNKNOWN_COUNTRY_CODE:
                country_name = u'Unknown Country'

            expected = [country_name, expected_percent_display, enrollment['count']]
            actual = [columns[0].text, columns[1].text, int(columns[2].text)]
            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[1].get_attribute('class'))

    def _test_metrics(self):
        """ Verify the metrics tiles display the correct information. """

        enrollment_data = [datum for datum in self.enrollment_data if datum['country']['name'] != 'UNKNOWN']
        self.assertSummaryPointValueEquals('data-stat-type=num-countries', unicode(len(enrollment_data)))

        for i in range(0, 3):
            country = enrollment_data[i]['country']['name']
            self.assertSummaryPointValueEquals('data-stat-type=top-country-{0}'.format((i + 1)), country)
