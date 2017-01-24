from bok_choy.web_app_test import WebAppTest

from acceptance_tests import TEST_COURSE_ID
from acceptance_tests.mixins import AnalyticsDashboardWebAppTestMixin
from acceptance_tests.pages import CourseIndexPage


_multiprocess_can_split_ = True


class CourseIndexTests(AnalyticsDashboardWebAppTestMixin, WebAppTest):
    test_skip_link_url = False

    def setUp(self):
        super(CourseIndexTests, self).setUp()
        self.page = CourseIndexPage(self.browser)

    def test_page(self):
        super(CourseIndexTests, self).test_page()
        self._test_course_list()

    def _test_course_list(self):
        """
        Course list should contain a link to the test course.
        """
        # text after the new line is only visible to screen readers
        columns = [
            'Course Name \nsort ascending',
            'Start Date \nclick to sort',
            'End Date \nclick to sort',
            'Total Enrollment \nclick to sort',
            'Current Enrollment \nclick to sort',
            'Change Last Week \nclick to sort',
            'Verified Enrollment \nclick to sort'
        ]
        self.assertTable('.course-list-table', columns)

        # Validate that we have a list of courses
        course_ids = self.page.q(css='.course-list .course-id')
        self.assertTrue(course_ids.present)

        # The element should list the test course id.
        self.assertIn(TEST_COURSE_ID, course_ids.text)

        # Validate the course links
        course_links = self.page.q(css='.course-list .course-name-cell a').attrs('href')

        for link, course_id in zip(course_links, course_ids):
            self.assertTrue(link.endswith(u'/courses/{}'.format(course_id.text)))
