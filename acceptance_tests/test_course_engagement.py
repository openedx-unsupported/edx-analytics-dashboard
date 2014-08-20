import datetime

from bok_choy.web_app_test import WebAppTest

from analyticsclient import activity_type as at

from acceptance_tests import AnalyticsApiClientMixin, FooterMixin
from acceptance_tests.pages import CourseEngagementPage


class CourseEngagementTests(AnalyticsApiClientMixin, FooterMixin, WebAppTest):
    """
    Tests for the Engagement page.
    """

    def setUp(self):
        """
        Instantiate the page object.
        """
        super(CourseEngagementTests, self).setUp()

        self.page = CourseEngagementPage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def test_page_exists(self):
        self.page.visit()

    def test_student_activity(self):
        self.page.visit()
        section_selector = "div[data-role=student-activity]"
        section = self.page.q(css=section_selector)
        self.assertTrue(section.present)

        # Verify the week displayed
        week = self.page.q(css=section_selector + ' span[data-role=activity-week]')
        self.assertTrue(week.present)
        expected = self.course.recent_activity(at.ANY)['interval_end']
        expected = datetime.datetime.strptime(expected, "%Y-%m-%dT%H:%M:%SZ")
        expected = expected.strftime('%B %d, %Y')
        self.assertEqual(week.text[0], expected)

        # Verify the activity values
        activity_types = [at.ANY, at.ATTEMPTED_PROBLEM, at.PLAYED_VIDEO, at.POSTED_FORUM]
        for activity_type in activity_types:
            selector = section_selector + ' div[data-activity-type=%s] .summary-point-number' % activity_type
            element = self.page.q(css=selector)
            self.assertTrue(element.present)
            self.assertEqual(int(element.text[0].replace(',', '')), self.course.recent_activity(activity_type)['count'])
