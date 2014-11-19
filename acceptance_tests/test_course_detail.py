from unittest import skipUnless

from bok_choy.web_app_test import WebAppTest
from acceptance_tests import ENABLE_COURSE_HOMEPAGE

from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CourseHomePage


_multiprocess_can_split_ = True


@skipUnless(ENABLE_COURSE_HOMEPAGE, 'Course homepage not enabled.')
class CourseHomeTests(CoursePageTestsMixin, WebAppTest):
    def setUp(self):
        super(CourseHomeTests, self).setUp()
        self.page = CourseHomePage(self.browser)
        self.course = self.api_client.courses(self.page.course_id)

    def _test_data_update_message(self):
        self.skipTest('The course homepage does not display any data.')
