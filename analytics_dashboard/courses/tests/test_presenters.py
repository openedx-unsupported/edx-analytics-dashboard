import mock
import datetime

from django.test import TestCase

import analyticsclient.activity_type as AT

from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter, BasePresenter
from courses.tests.utils import get_mock_enrollment_data, get_mock_enrollment_summary


def mock_activity_data(activity_type):
    activity_types = [AT.ANY, AT.ATTEMPTED_PROBLEM, AT.PLAYED_VIDEO, AT.POSTED_FORUM]

    summaries = {}
    count = 0
    for activity in activity_types:
        summaries[activity] = {
            'interval_end': 'this is a time ' + str(count),
            'activity_type': activity,
            'count': 500 * count
        }
        count += 1

    return summaries[activity_type]


class CourseEngagementPresenterTests(TestCase):
    @mock.patch('analyticsclient.course.Course.recent_activity',
                mock.Mock(side_effect=mock_activity_data, autospec=True))
    def test_get_summary(self):
        student_engagement = CourseEngagementPresenter()
        summary = student_engagement.get_summary('this/course/id')

        # make sure that we get the time from "ANY"
        self.assertEqual(summary['interval_end'], 'this is a time 0')

        # make sure that activity counts all match up
        self.assertEqual(summary[AT.ANY], 0)
        self.assertEqual(summary[AT.ATTEMPTED_PROBLEM], 500)
        self.assertEqual(summary[AT.PLAYED_VIDEO], 1000)
        self.assertEqual(summary[AT.POSTED_FORUM], 1500)


class BasePresenterTests(TestCase):
    def setUp(self):
        self.presenter = BasePresenter()

    def test_init(self):
        presenter = BasePresenter()
        self.assertEqual(presenter.client.timeout, 5)

        presenter = BasePresenter(timeout=15)
        self.assertEqual(presenter.client.timeout, 15)

    def test_parse_date(self):
        self.assertEqual(self.presenter.parse_date('2014-01-01'), datetime.date(year=2014, month=1, day=1))

    def test_format_date(self):
        self.assertEqual(self.presenter.format_date(datetime.date(year=2014, month=1, day=1)), '2014-01-01')


class CourseEnrollmentPresenterTests(TestCase):
    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.presenter = CourseEnrollmentPresenter(self.course_id)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(return_value=[]))
    def test_get_summary_no_data(self):
        actual = self.presenter.get_summary()
        expected = {
            'date': None,
            'current_enrollment': None,
            'enrollment_change_last_1_days': None,
            'enrollment_change_last_7_days': None,
            'enrollment_change_last_30_days': None,
        }

        self.assertDictEqual(actual, expected)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary(self, mock_enrollment):
        enrollment_data = get_mock_enrollment_data(self.course_id)
        mock_enrollment.side_effect = [[enrollment_data[-1]], enrollment_data]

        actual = self.presenter.get_summary()
        expected = get_mock_enrollment_summary()

        self.assertDictEqual(actual, expected)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_data(self, mock_enrollment):
        expected = get_mock_enrollment_data(self.course_id)
        mock_enrollment.return_value = expected
        actual = self.presenter.get_data(self.course_id)
        self.assertEqual(actual, expected)
