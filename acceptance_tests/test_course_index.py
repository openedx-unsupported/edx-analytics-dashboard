from bok_choy.web_app_test import WebAppTest
from acceptance_tests import AssertMixin, PrimaryNavMixin
from pages import CourseIndexPage

_multiprocess_can_split_ = True


class CourseIndexTests(WebAppTest, AssertMixin, PrimaryNavMixin):
    def setUp(self):
        super(CourseIndexTests, self).setUp()
        self.page = CourseIndexPage(self.browser)

    def test_page(self):
        self.page.visit()
        self._test_course_list()
        self._test_user_menu()

    def _test_course_list(self):
        """
        Course list should contain a link to the demo course.
        """
        course_id = 'edX/DemoX/Demo_Course'

        element = self.page.q(css='.course-list a')
        self.assertTrue(element.present)

        # The element should list the course ID.
        self.assertEqual(element.text[0], course_id)

        # The element should link to the course landing page.
        href = element.attrs('href')[0]
        self.assertTrue(href.endswith('/courses/{}/'.format(course_id)))

        # check that we have an email
        self.assertValidFeedbackLink('div[class=help-msg] a[class=feedback-email]')
