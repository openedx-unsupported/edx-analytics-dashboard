from unittest import skipUnless

from bok_choy.web_app_test import WebAppTest

from acceptance_tests import ENABLE_LEARNER_ANALYTICS
from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CourseLearnersPage


@skipUnless(ENABLE_LEARNER_ANALYTICS, 'Learner Analytics must be enabled to run CourseLearnersTests')
class CourseLearnersTests(CoursePageTestsMixin, WebAppTest):
    def setUp(self):
        super(CourseLearnersTests, self).setUp()
        self.page = CourseLearnersPage(self.browser)

    def _test_data_update_message(self):
        # Don't test the update message for now, since it won't exist
        # until the SPA adds it to the page in AN-6205.
        pass

    def _get_data_update_message(self):
        # Don't test the update message for now, since it won't exist
        # until the SPA adds it to the page in AN-6205.
        return ''
