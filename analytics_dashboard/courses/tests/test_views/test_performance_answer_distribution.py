import json

import mock
from ddt import ddt
from django.test import TestCase
from django.test.utils import override_settings

from courses.tests.test_views import ProblemViewTestMixin, COURSE_API_URL
from courses.tests import utils


@ddt
@override_settings(COURSE_API_URL=COURSE_API_URL)
class CoursePerformanceAnswerDistribution(ProblemViewTestMixin, TestCase):
    viewname = 'courses:performance_answer_distribution'
    presenter_method = 'courses.presenters.CoursePerformancePresenter.get_answer_distribution'

    @override_settings(LMS_COURSE_SHORTCUT_BASE_URL='a/url')
    def assertViewIsValid(self, course_id, problem_id, problem_part_id):
        rv = utils.get_presenter_answer_distribution(course_id, problem_part_id)
        with mock.patch(self.presenter_method, return_value=rv):
            assignment_id = 'i4x://MITx/4.605x_2/sequential/8084d006f7b54d79a5144c27cd672fae'
            response = self.client.get(self.path(course_id=course_id, assignment_id=assignment_id,
                                                 problem_id=problem_id, problem_part_id=problem_part_id))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        self.assertListEqual(context['questions'], rv.questions)
        self.assertDictContainsSubset({
            'page_title': 'Performance Answer Distribution',
            'problem_id': problem_id,
            'problem_part_id': problem_part_id,
            'view_live_url': 'a/url/{}/jump_to/{}'.format(course_id, problem_id),
            'active_question': rv.active_question,
        }, context)

        self.assertDictContainsSubset({
            'isRandom': rv.is_random,
            'answerType': rv.answer_type,
            'answerDistribution': rv.answer_distribution,
            'answerDistributionLimited': rv.answer_distribution_limited,
        }, json.loads(context['page_data'])['course'])

    def assertPrimaryNav(self, nav, course_id):
        # to be completed when course structure incorporated
        pass

    def assertSecondaryNavs(self, nav, course_id):
        # to be completed when course structure incorporated
        pass

    def get_mock_data(self, course_id):
        return utils.get_mock_api_answer_distribution_data(course_id)
