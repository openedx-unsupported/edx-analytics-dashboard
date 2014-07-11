from bok_choy.web_app_test import WebAppTest

from acceptance_tests.pages import CourseEnrollmentPage


class CourseEnrollmentTests(WebAppTest):
    """
    Tests for the Enrollment page.
    """

    def setUp(self):
        super(CourseEnrollmentTests, self).setUp()

        self.page = CourseEnrollmentPage(self.browser)

    def test_page_exists(self):
        self.page.visit()
