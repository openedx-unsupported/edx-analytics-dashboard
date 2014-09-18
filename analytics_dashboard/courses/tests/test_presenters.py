import mock
import datetime
from waffle import Switch

from django.test import TestCase

import analyticsclient.constants.activity_type as AT

from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter, BasePresenter
from courses.tests.utils import get_mock_enrollment_data, get_mock_enrollment_summary, \
    get_mock_api_enrollment_geography_data, get_mock_presenter_enrollment_geography_data


def mock_activity_data():
    # AT.POSTED_FORUM deliberately left off to test edge case where activity is empty
    activity_types = [AT.ANY, AT.ATTEMPTED_PROBLEM, AT.PLAYED_VIDEO]

    summaries = {
        'interval_end': '2014-01-01T000000',
    }
    count = 0
    for activity in activity_types:
        summaries[activity] = 500 * count
        count += 1

    return [summaries]


def mock_activity_trend_data(start_date=None, end_date=None):
    # pylint: disable=unused-argument
    return [
        {
            'interval_end': '2014-01-01T000000',
            AT.ANY: 100,
            AT.PLAYED_VIDEO: 200,
            AT.POSTED_FORUM: 300
        }, {
            'interval_end': '2014-01-07T000000',
            AT.ANY: 0,
            AT.ATTEMPTED_PROBLEM: 200,
            AT.POSTED_FORUM: 1234
        }
    ]


class CourseEngagementPresenterTests(TestCase):
    def setUp(self):
        super(CourseEngagementPresenterTests, self).setUp()
        self.presenter = CourseEngagementPresenter('this/course/id')

    def get_expected_trends(self, has_forum):
        trends = [
            {
                'weekEnding': '2014-01-01',
                AT.ANY: 100,
                AT.PLAYED_VIDEO: 200,
                AT.ATTEMPTED_PROBLEM: 0
            }, {
                'weekEnding': '2014-01-07',
                AT.ANY: 0,
                AT.PLAYED_VIDEO: 0,
                AT.ATTEMPTED_PROBLEM: 200
            }
        ]

        if has_forum:
            trends[0][AT.POSTED_FORUM] = 300
            trends[1][AT.POSTED_FORUM] = 1234

        return trends

    @mock.patch('analyticsclient.course.Course.activity', mock.Mock(side_effect=mock_activity_trend_data))
    def test_get_summary_and_trend_data(self):
        Switch.objects.create(name='show_engagement_forum_activity', active=True)
        expected_trends = self.get_expected_trends(True)
        summary, trends = self.presenter.get_summary_and_trend_data()

        # check the trends
        self.assertEqual(len(expected_trends), len(trends))
        self.assertDictEqual(expected_trends[0], trends[0])
        self.assertDictEqual(expected_trends[1], trends[1])

        # check the summary
        self.assertEqual(summary['interval_end'], datetime.date(year=2014, month=1, day=7))
        self.assertEqual(summary[AT.ANY], 0)
        self.assertIsNone(summary[AT.PLAYED_VIDEO])
        self.assertEqual(summary[AT.ATTEMPTED_PROBLEM], 200)
        self.assertEqual(summary[AT.POSTED_FORUM], 1234)

    def test_build_summary(self):
        Switch.objects.create(name='show_engagement_forum_activity', active=False)
        # pylint: disable=protected-access
        summary = self.presenter._build_summary(mock_activity_trend_data())

        # make sure that we get the time from "ANY"
        self.assertEqual(summary['interval_end'], datetime.date(year=2014, month=1, day=7))

        # make sure that activity counts all match up
        self.assertEqual(summary[AT.ANY], 0)
        self.assertIsNone(summary[AT.PLAYED_VIDEO])
        self.assertEqual(summary[AT.ATTEMPTED_PROBLEM], 200)

        # If an API query for a non-default activity type returns a 404, the presenter
        # returns nothing
        self.assertNotIn(AT.POSTED_FORUM, summary)

    def test_build_trend_data(self):
        Switch.objects.create(name='show_engagement_forum_activity', active=False)
        # pylint: disable=protected-access
        trends = self.presenter._build_trend(mock_activity_trend_data())
        expected_trends = self.get_expected_trends(False)

        # check the trends
        self.assertEqual(len(trends), len(expected_trends))
        self.assertDictEqual(trends[0], expected_trends[0])
        self.assertDictEqual(trends[1], expected_trends[1])


class BasePresenterTests(TestCase):
    def setUp(self):
        self.presenter = BasePresenter('edX/DemoX/Demo_Course')

    def test_init(self):
        presenter = BasePresenter('edX/DemoX/Demo_Course')
        self.assertEqual(presenter.client.timeout, 5)

        presenter = BasePresenter('edX/DemoX/Demo_Course', timeout=15)
        self.assertEqual(presenter.client.timeout, 15)

    def test_parse_date(self):
        self.assertEqual(self.presenter.parse_date('2014-01-01'), datetime.date(year=2014, month=1, day=1))

    def test_format_date(self):
        self.assertEqual(self.presenter.format_date(datetime.date(year=2014, month=1, day=1)), '2014-01-01')

    def test_parse_date_time_as_date(self):
        self.assertEqual(self.presenter.parse_date_time_as_date('2014-01-01T000000'),
                         datetime.date(year=2014, month=1, day=1))


class CourseEnrollmentPresenterTests(TestCase):
    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.presenter = CourseEnrollmentPresenter(self.course_id)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(return_value=[]))
    def test_get_trend_summary_no_data(self):
        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        expected_summary = {
            'date': None,
            'current_enrollment': None,
            'enrollment_change_last_7_days': None,
        }

        self.assertDictEqual(actual_summary, expected_summary)
        self.assertEqual(actual_trend, [])

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data(self, mock_enrollment):
        expected_trend = get_mock_enrollment_data(self.course_id)
        mock_enrollment.return_value = expected_trend
        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertEqual(actual_summary, get_mock_enrollment_summary())
        self.assertEqual(actual_trend, expected_trend)

    def test_build_summary(self):
        enrollment_data = get_mock_enrollment_data(self.course_id)

        # pylint: disable=protected-access
        actual = self.presenter._build_summary(enrollment_data)
        expected = get_mock_enrollment_summary()

        self.assertDictEqual(actual, expected)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_geography_data(self, mock_enrollment):
        mock_data = get_mock_api_enrollment_geography_data(self.course_id)
        mock_enrollment.return_value = mock_data
        expected_data, expected_update, expected_summary = get_mock_presenter_enrollment_geography_data()
        actual_data, last_updated, summary = self.presenter.get_geography_data()
        self.assertEqual(actual_data, expected_data)
        self.assertEqual(last_updated, expected_update)
        self.assertEqual(summary, expected_summary)
