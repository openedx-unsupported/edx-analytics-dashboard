from bok_choy.web_app_test import WebAppTest
from pages import CourseIndexPage


class CourseIndexTests(WebAppTest):
    def setUp(self):
        super(CourseIndexTests, self).setUp()
        self.page = CourseIndexPage(self.browser)

    def test_course_list(self):
        """
        Course list should contain a link to the demo course.
        """
        course_id = 'edX/DemoX/Demo_Course'

        self.page.visit()
        element = self.page.q(css='.course-list a')
        self.assertTrue(element.present)

        # The element should list the course ID.
        self.assertEqual(element.text[0], course_id)

        # The element should link to the course landing page.
        href = element.attrs('href')[0]
        self.assertTrue(href.endswith('/courses/{}/'.format(course_id)))
