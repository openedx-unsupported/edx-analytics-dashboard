from bok_choy.web_app_test import WebAppTest

from acceptance_tests import TEST_COURSE_ID
from acceptance_tests.mixins import AnalyticsDashboardWebAppTestMixin
from pages import CourseIndexPage


_multiprocess_can_split_ = True


class CourseIndexTests(AnalyticsDashboardWebAppTestMixin, WebAppTest):
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
        course_id = TEST_COURSE_ID
        course_name = self.get_course_name_or_id(course_id)

        # Validate that we have a list of course names
        course_names = self.page.q(css='.course-list .course a .course-name')
        self.assertTrue(course_names.present)

        # The element should list the test course name.
        self.assertIn(course_name, course_names.text)

        # Validate the course link
        index = course_names.text.index(course_name)
        course_links = self.page.q(css='.course-list .course a')
        href = course_links.attrs('href')[index]
        self.assertTrue(href.endswith(u'/courses/{}/'.format(course_id)))
