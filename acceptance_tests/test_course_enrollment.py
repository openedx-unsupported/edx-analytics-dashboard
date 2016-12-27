from collections import OrderedDict
import datetime

from analyticsclient.constants import demographic, UNKNOWN_COUNTRY_CODE, enrollment_modes
from bok_choy.web_app_test import WebAppTest

from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CourseEnrollmentActivityPage, CourseEnrollmentGeographyPage


_multiprocess_can_split_ = True


class CourseEnrollmentActivityTests(CoursePageTestsMixin, WebAppTest):
    help_path = 'enrollment/Enrollment_Activity.html'

    def setUp(self):
        super(CourseEnrollmentActivityTests, self).setUp()
        self.page = CourseEnrollmentActivityPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)

    def get_enrollment_data(self):
        """
        Returns all historical enrollment data for enrollment count collection.
        """
        end_date = datetime.datetime.utcnow()
        end_date_string = end_date.strftime(self.analytics_api_client.DATETIME_FORMAT)
        return self.course.enrollment('mode', start_date=None, end_date=end_date_string)

    def test_page(self):
        super(CourseEnrollmentActivityTests, self).test_page()
        self._test_enrollment_metrics_and_graph()
        self._test_enrollment_trend_table()

    def _get_data_update_message(self):
        current_enrollment = self.get_enrollment_data()[-1]
        last_updated = datetime.datetime.strptime(current_enrollment['created'], self.api_datetime_format)
        return 'Enrollment activity data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)

    def assertMetricTileValid(self, stat_type, value, tooltip):
        selector = 'data-stat-type=%s' % stat_type
        self.assertSummaryPointValueEquals(selector, self.format_number(value))
        self.assertSummaryTooltipEquals(selector, tooltip)

    def _get_valid_enrollment_modes(self, trends):
        valid_modes = set()
        invalid_modes = set(enrollment_modes.ALL)

        for datum in trends:
            for candidate in list(invalid_modes):
                if datum.get(candidate, 0) > 0:
                    invalid_modes.remove(candidate)
                    valid_modes.add(candidate)

            if len(invalid_modes) <= 0:
                break

        return valid_modes

    def _test_enrollment_metrics_and_graph(self):
        """ Verify the graph loads and that the metric tiles display the correct information. """

        enrollment_data = self.get_enrollment_data()
        enrollment = enrollment_data[-1]['count']

        # Verify the current enrollment metric tile.
        tooltip = u'Learners currently enrolled in the course.'
        self.assertMetricTileValid('current_enrollment', enrollment, tooltip)

        # Verify the total enrollment change metric tile.
        i = 7
        enrollment = enrollment - enrollment_data[-(i + 1)]['count']
        tooltip = u'Net difference in current enrollment in the last week.'
        self.assertMetricTileValid('enrollment_change_last_%s_days' % i, enrollment, tooltip)

        valid_modes = self._get_valid_enrollment_modes(enrollment_data)

        if enrollment_modes.VERIFIED in valid_modes:
            # Verify the verified enrollment metric tile.
            verified_enrollment = enrollment_data[-1][enrollment_modes.VERIFIED]
            tooltip = u'Number of currently enrolled learners pursuing a verified certificate of achievement.'
            self.assertMetricTileValid('verified_enrollment', verified_enrollment, tooltip)

        # Verify *something* rendered where the graph should be. We cannot easily verify what rendered
        self.assertElementHasContent("[data-section=enrollment-basics] #enrollment-trend-view")

    def _test_enrollment_trend_table(self):
        """ Verify the information rendered in the table is correct. """

        enrollment_data = sorted(self.get_enrollment_data(), reverse=True, key=lambda item: item['date'])

        table_selector = 'div[data-role=enrollment-table] table'
        headings = ['Date', 'Current Enrollment']

        valid_modes = self._get_valid_enrollment_modes(enrollment_data)
        display_names = OrderedDict([
            (enrollment_modes.HONOR, 'Honor'),
            (enrollment_modes.AUDIT, 'Audit'),
            (enrollment_modes.VERIFIED, 'Verified'),
            (enrollment_modes.PROFESSIONAL, 'Professional'),
            (enrollment_modes.CREDIT, 'Verified with Credit')
        ])
        for mode, display_name in display_names.items():
            if mode in valid_modes:
                headings.append(display_name)

        self.assertTableColumnHeadingsEqual(table_selector, headings)

        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = enrollment_data[i]
            expected_date = datetime.datetime.strptime(enrollment['date'], self.api_date_format).strftime("%B %d, %Y")
            expected_date = self.date_strip_leading_zeroes(expected_date)

            expected = [expected_date, self.format_number(enrollment['count'])]
            actual = [columns[0].text, columns[1].text]
            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[1].get_attribute('class'))

        # Verify CSV button has an href attribute
        selector = "a[data-role=enrollment-trend-csv]"
        self.assertValidHref(selector)


class CourseEnrollmentGeographyTests(CoursePageTestsMixin, WebAppTest):
    help_path = 'enrollment/Enrollment_Geography.html'

    def setUp(self):
        super(CourseEnrollmentGeographyTests, self).setUp()
        self.page = CourseEnrollmentGeographyPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
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
        return 'Geographic learner data was last updated %(update_date)s at %(update_time)s UTC.' % \
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
        self.assertTable(table_section_selector, ['Country or Region', 'Percent', 'Current Enrollment'],
                         'a[data-role=enrollment-location-csv]')

        rows = self.page.browser.find_elements_by_css_selector('{} tbody tr'.format(table_section_selector))
        sum_count = float(sum([datum['count'] for datum in self.enrollment_data]))

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            enrollment = self.enrollment_data[i]

            expected_percent_display = self.build_display_percentage(enrollment['count'], sum_count)

            country_name = enrollment['country']['name']
            if country_name == UNKNOWN_COUNTRY_CODE:
                country_name = u'Unknown Country'
            # FIXME: because django-countries is different between dashboard and api
            elif country_name == 'United States':
                country_name = u'United States of America'

            expected = [country_name, expected_percent_display, self.format_number(enrollment['count'])]
            actual = [columns[0].text, columns[1].text, columns[2].text]
            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[1].get_attribute('class'))

    def _test_metrics(self):
        """ Verify the metrics tiles display the correct information. """

        enrollment_data = [datum for datum in self.enrollment_data if datum['country']['name'] != 'UNKNOWN']
        self.assertSummaryPointValueEquals('data-stat-type=num-countries', unicode(len(enrollment_data)))

        for i in range(0, 3):
            country = enrollment_data[i]['country']['name']
            # FIXME: because django-countries is different between dashboard and api
            if country == 'United States':
                country = u'United Sta...'
            self.assertSummaryPointValueEquals('data-stat-type=top-country-{0}'.format((i + 1)), country)
