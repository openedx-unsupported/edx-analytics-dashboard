import datetime

from django.core.cache import cache
import mock
from django.test import TestCase, override_settings
import analyticsclient.constants.activity_type as AT

from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter, BasePresenter, \
    CourseEnrollmentDemographicsPresenter, CoursePerformancePresenter
from courses.tests import utils, SwitchMixin
from courses.tests.test_views import COURSE_API_URL
from courses.tests.utils import CoursePerformanceMockData


class CourseEngagementPresenterTests(SwitchMixin, TestCase):
    def setUp(self):
        super(CourseEngagementPresenterTests, self).setUp()
        self.presenter = CourseEngagementPresenter('this/course/id')

    def get_expected_trends(self, include_forum_data):
        trends = [
            {
                'weekEnding': '2014-08-31',
                AT.ANY: 1000,
                AT.ATTEMPTED_PROBLEM: 0,
                AT.PLAYED_VIDEO: 10000
            }, {
                'weekEnding': '2014-09-07',
                AT.ANY: 100,
                AT.ATTEMPTED_PROBLEM: 301,
                AT.PLAYED_VIDEO: 1000,

            }
        ]

        if include_forum_data:
            trends[0][AT.POSTED_FORUM] = 45
            trends[1][AT.POSTED_FORUM] = 0

        return trends

    def get_expected_trends_small(self, include_forum_data):
        trends = self.get_expected_trends(include_forum_data)
        trends[0].update({
            AT.ANY: 0,
            AT.ATTEMPTED_PROBLEM: 0,
            AT.PLAYED_VIDEO: 0
        })

        if include_forum_data:
            trends[0][AT.POSTED_FORUM] = 0

        return trends

    def assertSummaryAndTrendsValid(self, include_forum_activity, expected_trends):
        self.toggle_switch('show_engagement_forum_activity', include_forum_activity)

        summary, trends = self.presenter.get_summary_and_trend_data()

        # Validate the trends
        self.assertEqual(len(expected_trends), len(trends))
        self.assertDictEqual(expected_trends[0], trends[0])
        self.assertDictEqual(expected_trends[1], trends[1])

        # Validate the summary
        expected_summary = utils.mock_course_activity()[1]
        del expected_summary['created']
        del expected_summary['interval_end']
        del expected_summary['course_id']

        if not include_forum_activity:
            del expected_summary[AT.POSTED_FORUM]

        expected_summary['last_updated'] = utils.CREATED_DATETIME

        self.assertDictEqual(summary, expected_summary)

    @mock.patch('analyticsclient.course.Course.activity', mock.Mock(side_effect=utils.mock_course_activity))
    def test_get_summary_and_trend_data(self):
        self.assertSummaryAndTrendsValid(False, self.get_expected_trends(False))
        self.assertSummaryAndTrendsValid(True, self.get_expected_trends(True))

    @mock.patch('analyticsclient.course.Course.activity')
    def test_get_summary_and_trend_data_small(self, mock_activity):
        api_trend = [utils.mock_course_activity()[-1]]
        mock_activity.return_value = api_trend

        self.assertSummaryAndTrendsValid(False, self.get_expected_trends_small(False))
        self.assertSummaryAndTrendsValid(True, self.get_expected_trends_small(True))


class BasePresenterTests(TestCase):
    def setUp(self):
        self.presenter = BasePresenter('edX/DemoX/Demo_Course')

    def test_init(self):
        presenter = BasePresenter('edX/DemoX/Demo_Course')
        self.assertEqual(presenter.client.timeout, 15)

        presenter = BasePresenter('edX/DemoX/Demo_Course', timeout=15)
        self.assertEqual(presenter.client.timeout, 15)

    def test_parse_api_date(self):
        self.assertEqual(self.presenter.parse_api_date('2014-01-01'), datetime.date(year=2014, month=1, day=1))

    def test_parse_api_datetime(self):
        self.assertEqual(self.presenter.parse_api_datetime(u'2014-09-18T145957'),
                         datetime.datetime(year=2014, month=9, day=18, hour=14, minute=59, second=57))

    def test_strip_time(self):
        self.assertEqual(self.presenter.strip_time('2014-01-01T000000'), '2014-01-01')


class CourseEnrollmentPresenterTests(SwitchMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toggle_switch('display_verified_enrollment', True)

    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.presenter = CourseEnrollmentPresenter(self.course_id)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(return_value=[]))
    def test_get_trend_summary_no_data(self):
        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        expected_summary = {
            'last_updated': None,
            'current_enrollment': None,
            'enrollment_change_last_7_days': None,
        }

        self.assertDictEqual(actual_summary, expected_summary)
        self.assertEqual(actual_trend, [])

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data(self, mock_enrollment):
        mock_enrollment.return_value = utils.get_mock_api_enrollment_data(self.course_id)

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_enrollment_summary())

        expected_trend = utils.get_mock_presenter_enrollment_trend(self.course_id)
        self.assertListEqual(actual_trend, expected_trend)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data_with_gaps(self, mock_enrollment):
        """
        If the API returns data with gaps, get_summary_and_trend_data should fill in those gaps with data from the
        previous day.
        """
        gaps = utils.get_mock_api_enrollment_data_with_gaps(self.course_id)
        mock_enrollment.return_value = gaps

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_enrollment_summary())

        expected_trend = utils.get_mock_presenter_enrollment_trend_with_gaps_filled(self.course_id)
        self.assertListEqual(actual_trend, expected_trend)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data_small(self, mock_enrollment):
        """
        Verify the presenter responds appropriately when the course has a limited amount of data (e.g. one data point).
        """
        mock_enrollment.return_value = utils.get_mock_api_enrollment_data(self.course_id)[-1:]

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_presenter_enrollment_summary_small())
        self.assertListEqual(actual_trend, utils.get_mock_presenter_enrollment_data_small(self.course_id))

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_geography_data(self, mock_enrollment):
        mock_enrollment.return_value = utils.get_mock_api_enrollment_geography_data(self.course_id)

        expected_summary, expected_data = utils.get_mock_presenter_enrollment_geography_data()
        summary, actual_data = self.presenter.get_geography_data()

        self.assertDictEqual(summary, expected_summary)
        self.assertListEqual(actual_data, expected_data)

        # test with a small set of countries
        mock_data = utils.get_mock_api_enrollment_geography_data_limited(self.course_id)
        mock_enrollment.return_value = mock_data

        expected_summary, expected_data = utils.get_mock_presenter_enrollment_geography_data_limited()
        summary, actual_data = self.presenter.get_geography_data()

        self.assertDictEqual(summary, expected_summary)
        self.assertListEqual(actual_data, expected_data)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_hide_empty_enrollment_modes(self, mock_enrollment):
        """ Enrollment modes with no enrolled students should not be returned. """
        mock_enrollment.return_value = utils.get_mock_api_enrollment_data(self.course_id, include_verified=False)

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_enrollment_summary(include_verified=False))

        expected_trend = utils.get_mock_presenter_enrollment_trend(self.course_id, include_verified=False)
        self.assertListEqual(actual_trend, expected_trend)


class CourseEnrollmentDemographicsPresenterTests(TestCase):
    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.presenter = CourseEnrollmentDemographicsPresenter(self.course_id)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_gender(self, mock_gender):
        mock_data = utils.get_mock_api_enrollment_gender_data(self.course_id)
        mock_gender.return_value = mock_data

        last_updated, gender_data, trend, known_percent = self.presenter.get_gender()
        self.assertEqual(last_updated, utils.CREATED_DATETIME)
        self.assertListEqual(gender_data, utils.get_presenter_enrollment_gender_data())
        self.assertListEqual(trend, utils.get_presenter_enrollment_gender_trend(self.course_id))
        self.assertEqual(known_percent, 0.5)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_ages(self, mock_age):
        mock_data = utils.get_mock_api_enrollment_age_data(self.course_id)
        mock_age.return_value = mock_data

        last_updated, summary, binned_ages, known_percent = self.presenter.get_ages()

        self.assertEqual(last_updated, utils.CREATED_DATETIME)
        self.assertDictEqual(summary, utils.get_presenter_enrollment_ages_summary())
        print binned_ages
        print utils.get_presenter_enrollment_binned_ages()
        self.assertListEqual(binned_ages, utils.get_presenter_enrollment_binned_ages())
        self.assertEqual(known_percent, 0.5)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_education(self, mock_education):
        mock_data = utils.get_mock_api_enrollment_education_data(self.course_id)
        mock_education.return_value = mock_data

        last_updated, education_summary, education_levels, known_percent = self.presenter.get_education()

        self.assertEqual(last_updated, utils.CREATED_DATETIME)
        self.assertDictEqual(education_summary, utils.get_mock_presenter_enrollment_education_summary())
        self.assertListEqual(education_levels, utils.get_mock_presenter_enrollment_education_data())
        self.assertEqual(known_percent, 0.5)


@override_settings(COURSE_API_URL=COURSE_API_URL)
class CoursePerformancePresenterTests(TestCase):
    def setUp(self):
        cache.clear()
        self.course_id = 'edX/DemoX/Demo_Course'
        self.problem_id = 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36'
        self.presenter = CoursePerformancePresenter(self.course_id)

    @mock.patch('analyticsclient.module.Module.answer_distribution')
    def test_get_answer_distribution(self, mock_answer_distribution):

        mock_data = utils.get_mock_api_answer_distribution_data(self.course_id)
        mock_answer_distribution.return_value = mock_data

        problem_parts = [
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
                'expected': {
                    'active_question': 'Submissions for Part 1: Is this a text problem?',
                    'problem_part_description': 'Example problem - Submissions for Part 1: Is this a text problem?',
                    'is_random': False,
                    'answer_type': 'answer_value_text'
                }
            },
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1',
                'expected': {
                    'active_question': 'Submissions for Part 2: Is this a numeric problem?',
                    'problem_part_description': 'Example problem - Submissions for Part 2: Is this a numeric problem?',
                    'is_random': False,
                    'answer_type': 'answer_value_numeric'
                }
            },
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_4_1',
                'expected': {
                    'active_question': 'Submissions for Part 3: Is this a randomized problem?',
                    'problem_part_description': 'Example problem - Submissions for Part 3: Is this a '
                                                'randomized problem?',
                    'is_random': True,
                    'answer_type': 'answer_value_numeric'
                }
            }
        ]

        for part in problem_parts:
            expected = part['expected']

            # pylint: disable=line-too-long
            last_updated, questions, active_question, answer_distributions, answer_distribution_limited, is_random, answer_type, problem_part_description = self.presenter.get_answer_distribution(
                self.problem_id, part['part_id'])

            self.assertEqual(last_updated, utils.CREATED_DATETIME)
            self.assertListEqual(questions, utils.get_presenter_performance_answer_distribution_questions())
            self.assertEqual(problem_part_description, expected['problem_part_description'])
            self.assertEqual(active_question, expected['active_question'])
            self.assertEqual(answer_type, expected['answer_type'])
            self.assertEqual(is_random, expected['is_random'])

            expected_answer_distribution = utils.get_filtered_answer_distribution(self.course_id, part['part_id'])
            self.assertListEqual(answer_distributions, expected_answer_distribution)
            if is_random:
                self.assertIsNone(answer_distribution_limited)
            else:
                self.assertListEqual(answer_distribution_limited, expected_answer_distribution[:12])

    @mock.patch('slumber.Resource.get', mock.Mock(return_value=CoursePerformanceMockData.MOCK_GRADING_POLICY))
    def test_grading_policy(self):
        """ Verify the presenter returns the correct grading policy. """
        self.assertListEqual(self.presenter.grading_policy(), CoursePerformanceMockData.MOCK_GRADING_POLICY)

    @mock.patch('courses.presenters.CoursePerformancePresenter.grading_policy',
                mock.Mock(return_value=CoursePerformanceMockData.MOCK_GRADING_POLICY))
    def test_assignment_types(self):
        """ Verify the presenter returns the correct assignment types. """
        self.assertListEqual(self.presenter.assignment_types(), CoursePerformanceMockData.MOCK_ASSIGNMENT_TYPES)

    def _get_expected_assignments(self, assignment_type=None):
        assignments = CoursePerformanceMockData.MOCK_ASSIGNMENTS()

        # Filter by assignment type
        if assignment_type:
            assignment_type = assignment_type.lower()
            assignments = [assignment for assignment in assignments if
                           assignment['format'].lower() == assignment_type]

        # Add metadata and submission counts
        order = 1
        for assignment in assignments:
            # Use a more descriptive key name
            assignment['assignment_type'] = assignment.pop('format')

            problems = assignment['problems']
            num_problems = len(problems)
            for problem in problems:
                problem.update({
                    'total_submissions': 1,
                    'correct_submissions': 1,
                    'part_ids': []
                })
            assignment['num_problems'] = num_problems
            assignment['total_submissions'] = num_problems
            assignment['correct_submissions'] = num_problems
            assignment['order'] = order
            order += 1

        return assignments

    @mock.patch('slumber.Resource.get', mock.Mock(side_effect=CoursePerformanceMockData.MOCK_ASSIGNMENTS))
    def test_assignments(self):
        """ Verify the presenter returns the correct assignments. """

        with mock.patch('analyticsclient.module.Module.submission_counts', CoursePerformanceMockData.submission_counts):
            with mock.patch('analyticsclient.module.Module.part_ids', CoursePerformanceMockData.part_ids):
                # With no assignment type set, the method should return all assignment types.
                self.assertListEqual(self.presenter.assignments(), self._get_expected_assignments())

                # With an assignment type set, the presenter should return only the assignments of the specified type.
                for assignment_type in CoursePerformanceMockData.MOCK_ASSIGNMENT_TYPES:
                    cache.clear()
                    self.assertListEqual(self.presenter.assignments(assignment_type),
                                         self._get_expected_assignments(assignment_type))

    @mock.patch('courses.presenters.CoursePerformancePresenter.assignments',
                mock.Mock(return_value=CoursePerformanceMockData.MOCK_ASSIGNMENTS()))
    def test_assignment(self):
        """ Verify the presenter returns a specific assignment. """

        # The method should return None if the assignment does not exist.
        self.assertIsNone(self.presenter.assignment(None))
        self.assertIsNone(self.presenter.assignment('non-existent-id'))

        # The method should return an individual assignment if the ID exists.
        homework = CoursePerformanceMockData.HOMEWORK
        self.assertDictEqual(self.presenter.assignment(homework['id']), homework)
