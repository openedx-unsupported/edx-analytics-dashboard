from unittest import skipUnless
from bok_choy.web_app_test import WebAppTest
from acceptance_tests import ENABLE_COURSE_API
from mixins import CoursePageTestsMixin
from pages import CoursePerformanceGradedContentPage

_multiprocess_can_split_ = True


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test course performance pages.')
class CoursePerformanceGradedContentTests(CoursePageTestsMixin, WebAppTest):
    def _get_data_update_message(self):
        pass

    def _test_data_update_message(self):
        # There is no data update message displayed on this page.
        pass

    def _get_grading_policy(self):
        """
        Retrieve the course's grading policy from the Course API.
        """
        _field = u'raw_grader'
        raw = self.course_api_client.courses(self.page.course_id).get(include_fields=_field)[_field]
        policy = []

        for item in raw:
            policy.append({
                'type': item['type'],
                'count': item['min_count'],
                'weight': item['weight'],
                'dropped': item['drop_count']
            })

        return policy

    def setUp(self):
        super(CoursePerformanceGradedContentTests, self).setUp()
        self.page = CoursePerformanceGradedContentPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.grading_policy = self._get_grading_policy()

    def test_page(self):
        super(CoursePerformanceGradedContentTests, self).test_page()
        self._test_assignment_types()
        self._test_grading_configuration()

    def _test_assignment_types(self):
        # TODO Test the assignment type block sizes and labels
        self.fail()

    def _test_grading_configuration(self):
        # TODO Test the table contents
        self.fail()
