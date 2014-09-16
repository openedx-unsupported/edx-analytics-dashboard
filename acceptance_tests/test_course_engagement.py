import datetime

from bok_choy.web_app_test import WebAppTest
from bok_choy.promise import EmptyPromise

from analyticsclient import activity_type as at

from acceptance_tests import AnalyticsApiClientMixin, CoursePageTestsMixin, FooterMixin
from acceptance_tests.pages import CourseEngagementContentPage


_multiprocess_can_split_ = True


class CourseEngagementTests(AnalyticsApiClientMixin, FooterMixin, CoursePageTestsMixin, WebAppTest):
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

    def test_page_exists(self):
        self.page.visit()

    def test_engagement_summary(self):
        self.page.visit()
        section_selector = "div[data-role=student-activity]"

        section = self.page.q(css=section_selector)
        self.assertTrue(section.present)

        # Verify the week displayed
        week = self.page.q(css=section_selector + ' span[data-role=activity-week]')
        self.assertTrue(week.present)
        recent_activity = self.course.activity()[0]
        expected = recent_activity['interval_end']
        expected = datetime.datetime.strptime(expected, self.api_client.DATETIME_FORMAT)
        expected = expected.strftime('%B %d, %Y')
        self.assertEqual(week.text[0], expected)

        # Verify the activity values
        activity_types = [at.ANY, at.ATTEMPTED_PROBLEM, at.PLAYED_VIDEO]
        for activity_type in activity_types:
            selector = section_selector + ' div[data-activity-type=%s] .summary-point-number' % activity_type
            element = self.page.q(css=selector)
            self.assertTrue(element.present)
            self.assertEqual(int(element.text[0].replace(',', '')), self.course.recent_activity(activity_type)['count'])

    def test_engagement_graph(self):
        self.page.visit()
        # ensure that the trend data has finished loading
        graph_selector = '#engagement-trend-view'
        EmptyPromise(
            lambda: 'Loading Trend...' not in self.page.q(css=graph_selector + ' p').text,
            "Trend finished loading"
        ).fulfill()
        self.assertElementHasContent(graph_selector)

    def test_engagement_table(self):
        self.page.visit()
        date_time_format = self.api_client.DATETIME_FORMAT

        recent_activity = self.course.activity()[0]

        end_date = datetime.datetime.strptime(recent_activity['interval_end'], date_time_format) + datetime.timedelta(days=1)
        start_date_string = (end_date - datetime.timedelta(days=60)).strftime(self.api_client.DATE_FORMAT)
        end_date_string = end_date.strftime(self.api_client.DATE_FORMAT)

        trend_activity = self.course.activity(start_date=start_date_string, end_date=end_date_string)
        trend_activity = sorted(trend_activity, reverse=True, key=lambda item: item['interval_end'])

        table_selector = 'div[data-role=engagement-table] table'
        self.assertTableColumnHeadingsEqual(table_selector, ['Week Ending', 'Active Students', 'Tried a Problem', 'Watched a Video'])

        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            weekly_activity = trend_activity[i]
            expected_date = datetime.datetime.strptime(weekly_activity['interval_end'], date_time_format).strftime("%B %d, %Y").replace(' 0', ' ')
            expected = [expected_date, weekly_activity[at.ANY], weekly_activity[at.ATTEMPTED_PROBLEM], weekly_activity[at.PLAYED_VIDEO]]
            actual = [columns[0].text, int(columns[1].text), int(columns[2].text), int(columns[3].text)]
            self.assertListEqual(actual, expected)
            for j in range(1,4):
                self.assertIn('text-right', columns[j].get_attribute('class'))

        # Verify CSV button has an href attribute
        selector = "a[data-role=engagement-trend-csv]"
        self.assertValidHref(selector)
