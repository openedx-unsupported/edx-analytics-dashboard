import datetime

import mock
from django.test import TestCase
import analyticsclient.constants.activity_type as AT

from courses.presenters import BasePresenter
from courses.presenters.engagement import CourseEngagementPresenter
from courses.presenters.enrollment import CourseEnrollmentPresenter, CourseEnrollmentDemographicsPresenter
from courses.presenters.performance import CoursePerformancePresenter
from courses.tests import utils, SwitchMixin


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
        self.assertEqual(presenter.client.timeout, 5)

        presenter = BasePresenter('edX/DemoX/Demo_Course', timeout=15)
        self.assertEqual(presenter.client.timeout, 15)

    def test_parse_api_date(self):
        self.assertEqual(self.presenter.parse_api_date('2014-01-01'), datetime.date(year=2014, month=1, day=1))

    def test_parse_api_datetime(self):
        self.assertEqual(self.presenter.parse_api_datetime(u'2014-09-18T145957'),
                         datetime.datetime(year=2014, month=9, day=18, hour=14, minute=59, second=57))

    def test_strip_time(self):
        self.assertEqual(self.presenter.strip_time('2014-01-01T000000'), '2014-01-01')

    def test_get_current_date(self):
        dt_format = '%Y-%m-%d'
        self.assertEqual(self.presenter.get_current_date(), datetime.datetime.utcnow().strftime(dt_format))


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


class CoursePerformanceAnswerDistributionPresenterTests(TestCase):
    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.problem_id = 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36'
        self.presenter = CoursePerformancePresenter(self.course_id)

    @mock.patch('analyticsclient.module.Module.answer_distribution')
    def test_multiple_answer_distribution(self, mock_answer_distribution):

        mock_data = utils.get_mock_api_answer_distribution_multiple_questions_data(self.course_id)
        mock_answer_distribution.return_value = mock_data

        problem_parts = [
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
                'expected': {
                    'active_question': 'Submissions for Part 1: Is this a text problem?',
                    'problem_part_description': 'Part 1: Is this a text problem?',
                    'is_random': False,
                    'answer_type': 'text'
                }
            },
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1',
                'expected': {
                    'active_question': 'Submissions for Part 2: Is this a numeric problem?',
                    'problem_part_description': 'Part 2: Is this a numeric problem?',
                    'is_random': False,
                    'answer_type': 'numeric'
                }
            },
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_4_1',
                'expected': {
                    'active_question': 'Submissions for Part 3: Is this a randomized problem?',
                    'problem_part_description': 'Part 3: Is this a '
                                                'randomized problem?',
                    'is_random': True,
                    'answer_type': 'numeric'
                }
            }
        ]
        questions = utils.get_presenter_performance_answer_distribution_multiple_questions()
        self.assertAnswerDistribution(problem_parts, questions)

    @mock.patch('analyticsclient.module.Module.answer_distribution')
    def test_single_answer_distribution(self, mock_answer_distribution):

        mock_data = utils.get_mock_api_answer_distribution_single_question_data(self.course_id)
        mock_answer_distribution.return_value = mock_data

        problem_parts = [
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
                'expected': {
                    'active_question': 'Submissions: Is this a text problem?',
                    'problem_part_description': 'Is this a text problem?',
                    'is_random': False,
                    'answer_type': 'text'
                }
            }
        ]
        questions = utils.get_presenter_performance_answer_distribution_single_question()
        self.assertAnswerDistribution(problem_parts, questions)

    def assertAnswerDistribution(self, expected_problem_parts, expected_questions):
        for part in expected_problem_parts:
            expected = part['expected']
            answer_distribution_entry = self.presenter.get_answer_distribution(self.problem_id, part['part_id'])
            self.assertEqual(answer_distribution_entry.last_updated, utils.CREATED_DATETIME)
            self.assertListEqual(answer_distribution_entry.questions, expected_questions)
            self.assertEqual(answer_distribution_entry.problem_part_description, expected['problem_part_description'])
            self.assertEqual(answer_distribution_entry.active_question, expected['active_question'])
            self.assertEqual(answer_distribution_entry.answer_type, expected['answer_type'])
            self.assertEqual(answer_distribution_entry.is_random, expected['is_random'])

            expected_answer_distribution = utils.get_filtered_answer_distribution(self.course_id, part['part_id'])
            self.assertListEqual(answer_distribution_entry.answer_distribution, expected_answer_distribution)
            if answer_distribution_entry.is_random:
                self.assertIsNone(answer_distribution_entry.answer_distribution_limited)
            else:
                self.assertListEqual(answer_distribution_entry.answer_distribution_limited,
                                     expected_answer_distribution[:12])
