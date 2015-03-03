import json
import logging

from analyticsclient.exceptions import ClientError, NotFoundError
from ddt import ddt
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
import httpretty
from mock import patch, Mock, _is_started

from courses.tests import utils
from courses.tests.factories import CoursePerformanceDataFactory
from courses.tests.test_views import DEMO_COURSE_ID, CourseAPIMixin, NavAssertMixin, ViewTestMixin


logger = logging.getLogger(__name__)


@ddt
# pylint: disable=abstract-method
class CoursePerformanceViewTestMixin(CourseAPIMixin, NavAssertMixin, ViewTestMixin):
    patches = []

    def _patch(self, target, **mock_kwargs):
        self.patches.append(patch(target, Mock(**mock_kwargs)))

    def start_patching(self):
        for _patch in self.patches:
            _patch.start()

    def stop_patching(self):
        for _patch in self.patches:
            if _is_started(_patch):
                _patch.stop()

    def clear_patches(self):
        self.stop_patching()
        self.patches = []

    def setUp(self):
        super(CoursePerformanceViewTestMixin, self).setUp()
        self.toggle_switch('enable_course_api', True)
        self.factory = CoursePerformanceDataFactory()

        # Ensure patches from previous test failures are removed and de-referenced
        self.clear_patches()

        self._patch('courses.presenters.performance.CoursePerformancePresenter.assignments',
                    return_value=self.factory.present_assignments())
        self._patch('courses.presenters.performance.CoursePerformancePresenter.grading_policy',
                    return_value=self.factory.grading_policy)
        self.start_patching()

    def tearDown(self):
        super(CoursePerformanceViewTestMixin, self).tearDown()
        self.clear_patches()

    def get_mock_data(self, course_id):
        # The subclasses don't need this.
        pass

    def assertPrimaryNav(self, context, course_id):
        """
        Verifies that the Performance option is active in the main navigation bar.
        """
        nav = context['primary_nav_item']
        expected = {
            'icon': 'fa-check-square-o',
            'href': reverse('courses:performance:graded_content', kwargs={'course_id': course_id}),
            'label': _('Performance'),
            'name': 'performance'
        }
        self.assertDictEqual(nav, expected)

    def assertSecondaryNavs(self, context, course_id):
        """
        Verifies that the Graded Content option is active in the secondary navigation bar.
        """
        nav = context['secondary_nav_items']
        expected = [{'active': True, 'name': 'graded_content', 'label': _('Graded Content'), 'href': '#'}]
        self.assertListEqual(nav, expected)

    @httpretty.activate
    def test_valid_course(self):
        """
        The view should return HTTP 200 if the course is valid.

        Additional assertions should be added to validate page content.
        """

        course_id = DEMO_COURSE_ID

        # Mock the course details
        self.mock_course_detail(course_id)

        # Retrieve the page. Validate the status code and context.
        response = self.client.get(self.path(course_id=course_id))
        self.assertEqual(response.status_code, 200)
        self.assertValidContext(response.context)

        self.assertPrimaryNav(response.context, course_id)
        self.assertSecondaryNavs(response.context, course_id)

    @httpretty.activate
    def test_invalid_course(self):
        """
        The view should return HTTP 404 if the course is invalid.
        """
        self.stop_patching()

        course_id = 'fakeOrg/soFake/Fake_Course'
        self.grant_permission(self.user, course_id)
        self.mock_course_detail(course_id)
        path = self.path(course_id=course_id)

        # The course API would return a 404 for an invalid course. Simulate it to force an error in the view.
        api_path = 'grading_policies/{}/'.format(course_id)
        self.mock_course_api(api_path, status=404)

        response = self.client.get(path, follow=True)
        self.assertEqual(response.status_code, 404)

    def _test_api_error(self):
        # We need to break the methods that we normally patch.
        self.stop_patching()

        course_id = DEMO_COURSE_ID
        self.mock_course_detail(course_id)

        path = self.path(course_id=course_id)
        self.assertRaises(Exception, self.client.get, path, follow=True)

    @httpretty.activate
    @patch('analyticsclient.course.Course.problems', Mock(side_effect=ClientError))
    @patch('analyticsclient.module.Module.answer_distribution', Mock(side_effect=ClientError))
    def test_analytics_api_error(self):
        """
        The view should return HTTP 500 if the Analytics Data API fails (e.g. timeout, HTTP 5XX).
        """
        self._test_api_error()

    @httpretty.activate
    def test_course_api_error(self):
        """
        The view should return HTTP 500 if the Course API fails (e.g. timeout, HTTP 5XX).
        """
        # Nearly all course performance pages rely on retrieving the grading policy.
        # Break that endpoint to simulate an error.
        course_id = DEMO_COURSE_ID
        api_path = 'grading_policies/{}/'.format(course_id)
        self.mock_course_api(api_path, status=500)

        self._test_api_error()

    def assertValidContext(self, context):
        """
        Validates the response context.

        This is intended to be validate the context of a VALID response returned by a view under normal conditions.
        """
        expected = {
            'assignment_types': self.factory.assignment_types,
            'assignments': self.factory.present_assignments()
        }
        self.assertDictContainsSubset(expected, context)


@ddt
class CoursePerformanceAnswerDistributionViewTests(CoursePerformanceViewTestMixin, TestCase):
    viewname = 'courses:performance:answer_distribution'
    presenter_method = 'courses.presenters.performance.CoursePerformancePresenter.get_answer_distribution'

    PROBLEM_ID = 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36'
    TEXT_PROBLEM_PART_ID = 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1'
    NUMERIC_PROBLEM_PART_ID = 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1'
    RANDOMIZED_PROBLEM_PART_ID = 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1'

    def path(self, **kwargs):
        # Use default kwargs for tests that don't necessarily care about the specific argument values.
        default_kwargs = {
            'assignment_id': self.factory.assignments[0][u'id'],
            'problem_id': self.PROBLEM_ID,
            'problem_part_id': self.TEXT_PROBLEM_PART_ID
        }
        default_kwargs.update(kwargs)
        kwargs = default_kwargs

        return super(CoursePerformanceAnswerDistributionViewTests, self).path(**kwargs)

    @httpretty.activate
    def test_valid_course(self):
        course_id = DEMO_COURSE_ID

        # Mock the course details
        self.mock_course_detail(course_id)

        # Mock the problem response used to populate the navbar.
        with patch('courses.presenters.performance.CoursePerformancePresenter.problem',
                   return_value=self.factory.present_assignments()[0]['problems'][0]):
            # API returns different data (e.g. text answers, numeric answers, and randomized answers), resulting in
            # different renderings for these problem part IDs.
            for problem_part_id in [self.TEXT_PROBLEM_PART_ID, self.NUMERIC_PROBLEM_PART_ID,
                                    self.RANDOMIZED_PROBLEM_PART_ID]:
                logger.info('Testing answer distribution view with problem_part_id: %s', problem_part_id)
                self.assertViewIsValid(course_id, self.PROBLEM_ID, problem_part_id)

    def assertViewIsValid(self, course_id, problem_id, problem_part_id):
        # Retrieve a mock assignment ID
        assignment_id = self.factory.assignments[0][u'id']

        # Mock the answer distribution and retrieve the view
        rv = utils.get_presenter_answer_distribution(course_id, problem_part_id)
        with patch(self.presenter_method, return_value=rv):
            response = self.client.get(self.path(course_id=course_id, assignment_id=assignment_id,
                                                 problem_id=problem_id, problem_part_id=problem_part_id))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)
        self.assertValidContext(response.context)

        self.assertListEqual(context['questions'], rv.questions)
        self.assertDictContainsSubset(
            {
                'page_title': 'Performance: Problem Submissions',
                'problem_id': problem_id,
                'problem_part_id': problem_part_id,
                'view_live_url': '{}/{}/jump_to/{}'.format(settings.LMS_COURSE_SHORTCUT_BASE_URL, course_id,
                                                           problem_id),
                'active_question': rv.active_question,
                'questions': rv.questions
            }, context)
        self.assertDictContainsSubset(
            {
                'isRandom': rv.is_random,
                'answerType': rv.answer_type,
                'answerDistribution': rv.answer_distribution,
                'answerDistributionLimited': rv.answer_distribution_limited,
            }, json.loads(context['page_data'])['course'])

        self.assertPrimaryNav(response.context, course_id)
        self.assertSecondaryNavs(response.context, course_id)

    @httpretty.activate
    @patch(presenter_method, Mock(side_effect=NotFoundError))
    def test_missing_distribution_data(self):
        """
        The view should return HTTP 404 if the answer distribution data is missing.
        """

        course_id = DEMO_COURSE_ID

        # Mock the course details
        self.mock_course_detail(course_id)

        response = self.client.get(self.path(course_id=course_id))
        self.assertEqual(response.status_code, 404)


class CoursePerformanceGradedContentViewTests(CoursePerformanceViewTestMixin, TestCase):
    viewname = 'courses:performance:graded_content'

    def assertValidContext(self, context):
        # We intentionally do not call the superclass method since this page does not have
        # an assignments field in the context.

        expected = {
            'assignment_types': self.factory.assignment_types,
            'grading_policy': self.factory.grading_policy,
        }
        self.assertDictContainsSubset(expected, context)


class CoursePerformanceGradedContentByTypeViewTests(CoursePerformanceViewTestMixin, TestCase):
    viewname = 'courses:performance:graded_content_by_type'

    def setUp(self):
        super(CoursePerformanceGradedContentByTypeViewTests, self).setUp()
        self.assignment_type = self.factory.assignment_types[0]

    def path(self, **kwargs):
        # Use default kwargs for tests that don't necessarily care about the specific argument values.
        default_kwargs = {
            'assignment_type': self.assignment_type,
        }
        default_kwargs.update(kwargs)
        kwargs = default_kwargs

        return super(CoursePerformanceGradedContentByTypeViewTests, self).path(**kwargs)

    def assertValidContext(self, context):
        super(CoursePerformanceGradedContentByTypeViewTests, self).assertValidContext(context)
        self.assertEqual(self.assignment_type, context['assignment_type'])

    @httpretty.activate
    @patch('courses.presenters.performance.CoursePerformancePresenter.assignments', Mock(return_value=[]))
    def test_missing_assignments(self):
        """
        The view should return HTTP 200 if there are no assignments. The template will adjust to inform the user
        of the issue.

        Assignments might be missing if the assignment type is invalid or the course is incomplete.
        """

        course_id = DEMO_COURSE_ID

        # Mock the course details
        self.mock_course_detail(course_id)

        response = self.client.get(self.path(course_id=course_id, assignment_type='Invalid'))
        self.assertEqual(response.status_code, 200)


class CoursePerformanceAssignmentViewTests(CoursePerformanceViewTestMixin, TestCase):
    viewname = 'courses:performance:assignment'

    def setUp(self):
        super(CoursePerformanceAssignmentViewTests, self).setUp()
        self.assignment = self.factory.present_assignments()[0]
        self.assignment_type = self.assignment['assignment_type']

    def path(self, **kwargs):
        # Use default kwargs for tests that don't necessarily care about the specific argument values.
        default_kwargs = {
            'assignment_id': self.assignment['id'],
        }
        default_kwargs.update(kwargs)
        kwargs = default_kwargs

        return super(CoursePerformanceAssignmentViewTests, self).path(**kwargs)

    def assertValidContext(self, context):
        super(CoursePerformanceAssignmentViewTests, self).assertValidContext(context)

        self.assertListEqual(context['js_data']['course']['problems'], self.assignment['problems'])
        expected = {
            'assignment_type': self.assignment_type,
            'assignment': self.assignment,
        }
        self.assertDictContainsSubset(expected, context)

    @httpretty.activate
    @patch('courses.presenters.performance.CoursePerformancePresenter.assignment', Mock(return_value=None))
    def test_missing_assignment(self):
        """
        The view should return HTTP 404 if the assignment is not found.

        Assignments might be missing if the assignment type is invalid or the course is incomplete.
        """

        course_id = DEMO_COURSE_ID

        # Mock the course details
        self.mock_course_detail(course_id)

        response = self.client.get(self.path(course_id=course_id, assignment_id='Invalid'))
        self.assertEqual(response.status_code, 404)
