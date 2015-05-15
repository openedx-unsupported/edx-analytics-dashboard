import datetime
from unittest import skipUnless

from analyticsclient.constants import activity_type as at
from bok_choy.web_app_test import WebAppTest

from acceptance_tests import (ENABLE_COURSE_API, ENABLE_FORUM_POSTS)
from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import (
    CourseEngagementContentPage,
    CourseEngagementVideosContentPage,
    CourseEngagementVideoSectionPage,
    CourseEngagementVideoSubsectionPage)


_multiprocess_can_split_ = True


# pylint: disable=abstract-method
class CourseEngagementPageTestsMixin(CoursePageTestsMixin):
    help_path = 'engagement/Engagement_Content.html'
    chart_selector = None

    def test_page(self):
        super(CourseEngagementPageTestsMixin, self).test_page()
        self._test_chart()
        self._test_table()

    def _test_chart(self):
        # Ensure the graph is loaded via AJAX
        self.fulfill_loading_promise(self.chart_selector)
        self.assertElementHasContent(self.chart_selector)

    def _test_table(self):
        raise NotImplementedError


class CourseEngagementContentTests(CourseEngagementPageTestsMixin, WebAppTest):
    """
    Tests for the Engagement content page.
    """

    chart_selector = '#engagement-trend-view'

    def setUp(self):
        """
        Instantiate the page object.
        """
        super(CourseEngagementContentTests, self).setUp()
        self.page = CourseEngagementContentPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)

    def test_page(self):
        super(CourseEngagementContentTests, self).test_page()
        self._test_engagement_metrics()

    def _get_data_update_message(self):
        recent_activity = self.course.activity()[0]
        last_updated = datetime.datetime.strptime(recent_activity['created'], self.api_datetime_format)
        return 'Course engagement data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)

    def _test_engagement_metrics(self):
        """ Verify the metrics tiles display the correct information. """
        end_date = datetime.datetime.utcnow().strftime(self.analytics_api_client.DATE_FORMAT)
        recent_activity = self.course.activity(end_date=end_date)[-1]

        # Verify the activity values
        activity_types = [at.ANY, at.ATTEMPTED_PROBLEM, at.PLAYED_VIDEO]
        expected_tooltips = {
            at.ANY: u'Students who visited at least one page in the course content.',
            at.ATTEMPTED_PROBLEM: u'Students who submitted an answer for a standard problem. '
                                  u'Not all problem types are included.',
            at.PLAYED_VIDEO: u'Students who played one or more videos.'
        }
        for activity_type in activity_types:
            data_selector = 'data-activity-type={0}'.format(activity_type)
            self.assertSummaryPointValueEquals(data_selector, self.format_number(recent_activity[activity_type]))
            self.assertSummaryTooltipEquals(data_selector, expected_tooltips[activity_type])

    def _test_table(self):
        """ Verify the activity table is rendered with the correct information. """
        date_time_format = self.analytics_api_client.DATETIME_FORMAT

        end_date = datetime.datetime.utcnow()
        end_date_string = end_date.strftime(self.analytics_api_client.DATE_FORMAT)

        trend_activity = self.course.activity(start_date=None, end_date=end_date_string)
        trend_activity = sorted(trend_activity, reverse=True, key=lambda item: item['interval_end'])

        table_selector = 'div[data-role=engagement-table] table'

        headings = [u'Week Ending', u'Active Students', u'Watched a Video', u'Tried a Problem']
        if ENABLE_FORUM_POSTS:
            headings.append(u'Posted in Forum')

        self.assertTableColumnHeadingsEqual(table_selector, headings)

        rows = self.page.browser.find_elements_by_css_selector('%s tbody tr' % table_selector)
        self.assertGreater(len(rows), 0)

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            weekly_activity = trend_activity[i]
            expected_date = self.format_time_as_dashboard(
                (datetime.datetime.strptime(weekly_activity['interval_end'], date_time_format)) - datetime.timedelta(
                    days=1))
            expected_date = self.date_strip_leading_zeroes(expected_date)
            expected = [expected_date,
                        self.format_number(weekly_activity[at.ANY]),
                        self.format_number(weekly_activity[at.PLAYED_VIDEO]),
                        self.format_number(weekly_activity[at.ATTEMPTED_PROBLEM])]
            actual = [columns[0].text, columns[1].text, columns[2].text, columns[3].text]
            self.assertListEqual(actual, expected)

            for j in range(1, 4):
                self.assertIn('text-right', columns[j].get_attribute('class'))

        # Verify CSV button has an href attribute
        selector = "a[data-role=engagement-trend-csv]"
        self.assertValidHref(selector)


# pylint: disable=abstract-method
class CourseEngagementVideoMixin(CourseEngagementPageTestsMixin):
    help_path = 'engagement/Engagement_Video.html'
    chart_selector = '#chart-view'
    expected_heading = None
    expected_tooltip = None
    expected_table_columns = None

    def test_page(self):
        super(CourseEngagementVideoMixin, self).test_page()
        self._test_heading_question()

    def _get_data_update_message(self):
        videos = self.course.videos()
        last_updated = datetime.datetime.min

        for video in videos:
            last_updated = max(last_updated, datetime.datetime.strptime(video['created'], self.api_datetime_format))

        updated_date_and_time = self.format_last_updated_date_and_time(last_updated)
        return ('Video data was last updated {} at {} UTC.').format(
            updated_date_and_time['update_date'], updated_date_and_time['update_time'])

    def _test_table(self):
        element = self.page.q(css='.section-title')
        self.assertIn(u'Video Plays', element[0].text)
        self.assertTableColumnHeadingsEqual('div[data-role="data-table"]', self.expected_table_columns)

    def _test_chart(self):
        super(CourseEngagementVideoMixin, self)._test_chart()
        container_selector = '.analytics-chart-container'
        element = self.page.q(css=container_selector + ' i')
        self.assertEqual(element[0].get_attribute('data-original-title'), self.expected_tooltip)

    def _test_heading_question(self):
        element = self.page.q(css='.section-heading')
        self.assertEqual(element.text[0], self.expected_heading)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the video pages.')
class CourseEngagementVideoContentTests(CourseEngagementVideoMixin, WebAppTest):
    expected_heading = u'How did students interact with course videos?'
    expected_tooltip = u'Each bar shows the counts of complete and incomplete plays of the videos in that section. ' \
                       u'Click on bars with low totals or a high incomplete rate to drill down and understand ' \
                       u'why.'
    expected_table_columns = [u'Order', u'Section Name', u'Videos', u'Started Watching', u'Finished Watching',
                              u'Completion Percentage']

    def setUp(self):
        super(CourseEngagementVideoContentTests, self).setUp()
        self.page = CourseEngagementVideosContentPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the video pages.')
class CourseEngagementVideoSectionTests(CourseEngagementVideoMixin, WebAppTest):
    expected_heading = u'How did students interact with videos in this section?'
    expected_tooltip = u'Each bar shows the counts of complete and incomplete plays of the videos in that ' \
                       u'subsection. Click on bars with low totals or a high incomplete rate to drill down and ' \
                       u'understand why.'
    expected_table_columns = [u'Order', u'Subsection Name', u'Videos', u'Started Watching', u'Finished Watching',
                              u'Completion Percentage']

    def setUp(self):
        super(CourseEngagementVideoSectionTests, self).setUp()
        self.page = CourseEngagementVideoSectionPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the video pages.')
class CourseEngagementVideoSubsectionTests(CourseEngagementVideoMixin, WebAppTest):
    expected_heading = u'How did students interact with videos in this subsection?'
    expected_tooltip = u'Each bar shows the counts of complete and incomplete plays for that video. ' \
                       u'Click to understand where students drop off and which parts they replay.'
    expected_table_columns = [u'Order', u'Video Name', u'Started Watching', u'Finished Watching',
                              u'Completion Percentage']

    def setUp(self):
        super(CourseEngagementVideoSubsectionTests, self).setUp()
        self.page = CourseEngagementVideoSubsectionPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
