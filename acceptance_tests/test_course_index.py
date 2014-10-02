from bok_choy.web_app_test import WebAppTest
from acceptance_tests import TEST_COURSE_ID
from acceptance_tests.mixins import AssertMixin, PrimaryNavMixin, LoginMixin
from pages import CourseIndexPage

_multiprocess_can_split_ = True


class CourseIndexTests(AssertMixin, PrimaryNavMixin, LoginMixin, WebAppTest):
    def setUp(self):
        super(CourseIndexTests, self).setUp()
        self.page = CourseIndexPage(self.browser)

    def test_page(self):
        self.login()
        self.page.visit()
        self._test_course_list()
        self._test_user_menu()

    def _test_course_list(self):
        """
        Course list should contain a link to the demo course.
        """
        course_id = TEST_COURSE_ID

        element = self.page.q(css='.course-list a')
        self.assertTrue(element.present)

        # The element should list the test course ID.
        self.assertIn(course_id, element.text)

        # The element should link to the course landing page.
        index = element.text.index(course_id)
        href = element.attrs('href')[index]
        self.assertTrue(href.endswith('/courses/{}/'.format(course_id)))

        # check that we have an email
        self.assertValidFeedbackLink('div[class=help-msg] a[class=feedback-email]')
