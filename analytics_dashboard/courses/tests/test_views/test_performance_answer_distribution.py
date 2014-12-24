import json
import mock
from ddt import ddt

from django.test import TestCase
from django.test.utils import override_settings

from courses.tests.test_views import ProblemViewTestMixin
from courses.tests import utils


@ddt
class CoursePerformanceAnswerDistribution(ProblemViewTestMixin, TestCase):
    viewname = 'courses:performance_answerdistribution'
    presenter_method = 'courses.presenters.CoursePerformancePresenter.get_answer_distribution'

    @override_settings(LMS_COURSE_JUMP_TO_BASE_URL='a/url')
    def assertViewIsValid(self, course_id, problem_id, problem_part_id):
        rv = utils.get_presenter_answer_distribution(course_id, problem_part_id)
        with mock.patch(self.presenter_method, return_value=rv):
            response = self.client.get(self.path({
                'course_id': course_id,
                'content_id': problem_id,
                'problem_part_id': problem_part_id
            }))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        self.assertEqual(context['page_title'], 'Performance Answer Distribution')
        self.assertEqual(context['problem_id'], problem_id)
        self.assertEqual(context['problem_part_id'], problem_part_id)
        self.assertEqual(context['jump_to_url'], 'a/url/{}/jump_to/{}'.format(course_id, problem_id))
        self.assertListEqual(context['questions'], rv.questions)
        self.assertEqual(context['active_question'], rv.active_question)

        js_data = json.loads(context['page_data'])['course']
        self.assertEqual(js_data['isRandom'], rv.is_random)
        self.assertEqual(js_data['answerType'], rv.answer_type)
        self.assertEqual(js_data['answerDistribution'], rv.answer_distribution)
        self.assertEqual(js_data['answerDistributionLimited'], rv.answer_distribution_limited)

    def assertPrimaryNav(self, nav, course_id):
        # to be completed when course structure incorporated
        pass

    def assertSecondaryNavs(self, nav, course_id):
        # to be completed when course structure incorporated
        pass

    def get_mock_data(self, course_id):
        return utils.get_mock_api_answer_distribution_data(course_id)
