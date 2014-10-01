import datetime

from bok_choy.web_app_test import WebAppTest

from analyticsclient.constants import activity_type as at
from acceptance_tests import CoursePageTestsMixin
from acceptance_tests.pages import CourseEngagementContentPage


_multiprocess_can_split_ = True


class CourseEngagementTests(CoursePageTestsMixin, WebAppTest):
    """
    Tests for the Engagement page.
    """

    def setUp(self):
        """
        Instantiate the page object.
        """
        super(CourseEngagementTests, self).setUp()

        self.page = CourseEngagementContentPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def test_page(self):
        super(CourseEngagementTests, self).test_page()
        self._test_engagement_metrics()
        self._test_engagement_graph()
        self._test_engagement_table()

    def _get_data_update_message(self):
        recent_activity = self.course.activity()[0]
        last_updated = datetime.datetime.strptime(recent_activity['created'], self.api_datetime_format)
        return 'Course engagement data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)

    def _test_engagement_metrics(self):
        """ Verify the metrics tiles display the correct information. """
        end_date = datetime.datetime.utcnow().strftime(self.api_client.DATE_FORMAT)
        recent_activity = self.course.activity(end_date=end_date)[-1]

        # Verify the activity values
        activity_types = [at.ANY, at.ATTEMPTED_PROBLEM, at.PLAYED_VIDEO]
        expected_tooltips = {
            at.ANY: u'Students who visited at least one page in the course content.',
            at.ATTEMPTED_PROBLEM: u'Students who submitted an answer for a standard problem. Not all problem types are included.',
            at.PLAYED_VIDEO: u'Students who played one or more videos.'
        }
        for activity_type in activity_types:
            data_selector = 'data-activity-type={0}'.format(activity_type)
            self.assertSummaryPointValueEquals(data_selector, unicode(recent_activity[activity_type]))
            self.assertSummaryTooltipEquals(data_selector, expected_tooltips[activity_type])

    def _test_engagement_graph(self):
        """ Verify the graph is rendered. """

        graph_selector = '#engagement-trend-view'

        # Ensure the graph is loaded via AJAX
        self.fulfill_loading_promise(graph_selector)

        self.assertElementHasContent(graph_selector)

    def _test_engagement_table(self):
        """ Verify the activity table is rendered with the correct information. """
        date_time_format = self.api_client.DATETIME_FORMAT

        end_date = datetime.datetime.utcnow()
        end_date_string = end_date.strftime(self.api_client.DATE_FORMAT)

        trend_activity = self.course.activity(start_date=None, end_date=end_date_string)
        trend_activity = sorted(trend_activity, reverse=True, key=lambda item: item['interval_end'])

        table_selector = 'div[data-role=engagement-table] table'
        self.assertTableColumnHeadingsEqual(table_selector, [u'Week Ending', u'Active Students', u'Watched a Video',
                                                             u'Tried a Problem'])

        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            weekly_activity = trend_activity[i]
            expected_date = self.format_time_as_dashboard((
                datetime.datetime.strptime(weekly_activity['interval_end'], date_time_format)) - datetime.timedelta(days=1)).replace(' 0', ' ')
            expected = [expected_date, weekly_activity[at.ANY], weekly_activity[at.PLAYED_VIDEO],
                        weekly_activity[at.ATTEMPTED_PROBLEM]]
            actual = [columns[0].text, int(columns[1].text), int(columns[2].text), int(columns[3].text)]
            self.assertListEqual(actual, expected)

            for j in range(1, 4):
                self.assertIn('text-right', columns[j].get_attribute('class'))

        # Verify CSV button has an href attribute
        selector = "a[data-role=engagement-trend-csv]"
        self.assertValidHref(selector)
