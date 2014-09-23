import datetime

import mock
from waffle import Switch
from django.test import TestCase

import analyticsclient.constants.activity_type as AT
from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter, BasePresenter
from courses.tests.utils import get_mock_enrollment_data, get_mock_enrollment_summary, \
    get_mock_api_enrollment_geography_data, get_mock_presenter_enrollment_geography_data, \
    get_mock_api_enrollment_geography_data_limited, get_mock_presenter_enrollment_geography_data_limited, \
    mock_course_activity, CREATED_DATETIME


class CourseEngagementPresenterTests(TestCase):
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

    def assertSummaryAndTrendsValid(self, include_forum_activity):
        switch, _created = Switch.objects.get_or_create(name='show_engagement_forum_activity')
        switch.active = include_forum_activity
        switch.save()

        expected_trends = self.get_expected_trends(include_forum_activity)
        summary, trends = self.presenter.get_summary_and_trend_data()

        # Validate the trends
        self.assertEqual(len(expected_trends), len(trends))
        self.assertDictEqual(expected_trends[0], trends[0])
        self.assertDictEqual(expected_trends[1], trends[1])

        # Validate the summary
        expected_summary = mock_course_activity()[1]
        del expected_summary['created']
        del expected_summary['interval_end']

        if not include_forum_activity:
            del expected_summary[AT.POSTED_FORUM]

        expected_summary['last_updated'] = CREATED_DATETIME

        self.assertDictEqual(summary, expected_summary)

    @mock.patch('analyticsclient.course.Course.activity', mock.Mock(side_effect=mock_course_activity))
    def test_get_summary_and_trend_data(self):
        self.assertSummaryAndTrendsValid(False)
        self.assertSummaryAndTrendsValid(True)


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


class CourseEnrollmentPresenterTests(TestCase):
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
        expected_trend = get_mock_enrollment_data(self.course_id)
        mock_enrollment.return_value = expected_trend

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, get_mock_enrollment_summary())
        self.assertListEqual(actual_trend, expected_trend)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_geography_data(self, mock_enrollment):
        mock_enrollment.return_value = get_mock_api_enrollment_geography_data(self.course_id)

        expected_summary, expected_data = get_mock_presenter_enrollment_geography_data()
        summary, actual_data = self.presenter.get_geography_data()

        self.assertDictEqual(summary, expected_summary)
        self.assertListEqual(actual_data, expected_data)

        # test with a small set of countries
        mock_data = get_mock_api_enrollment_geography_data_limited(self.course_id)
        mock_enrollment.return_value = mock_data

        expected_summary, expected_data = get_mock_presenter_enrollment_geography_data_limited()
        summary, actual_data = self.presenter.get_geography_data()

        self.assertDictEqual(summary, expected_summary)
        self.assertListEqual(actual_data, expected_data)
