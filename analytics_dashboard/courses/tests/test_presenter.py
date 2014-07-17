import mock
import datetime

from django.test import TestCase

import analyticsclient.activity_type as AT

from courses.presenters import StudentEngagement, StudentEnrollment


def mock_enrollment_data_empty(demographic=None, start_date=None, end_date=None):
    return []

def mock_enrollment_data_full(demographic=None, start_date=None, end_date=None):
    if start_date is None:
        start_date = '2014-04-23'
        end_date = '2014-04-24'

    start = datetime.datetime.strptime(start_date, StudentEnrollment.DATE_FORMAT)
    end = datetime.datetime.strptime(end_date, StudentEnrollment.DATE_FORMAT)
    days_past = (end-start).days

    data = []

    # create the dates
    date_list = [end - datetime.timedelta(days=x) for x in range(0, days_past)][::-1]
    for date in date_list:
        data.append({'date': date.strftime(StudentEnrollment.DATE_FORMAT)})

    # fill in the counts
    for count in range(0,len(data))[::-1]:
        i = len(data)-count-1
        data[i]['count'] = count

    return data


def mock_activity_data(activity_type):
    activity_types = [AT.ANY, AT.ATTEMPTED_PROBLEM, AT.PLAYED_VIDEO,
                      AT.POSTED_FORUM]

    summaries = {}
    count = 0
    for activity in activity_types:
        summaries[activity] = {
            'interval_end': 'this is a time ' + str(count),
            'activity_type': activity,
            'count': 500 * count
        }
        count = count + 1

    return summaries[activity_type]

class StudentEngagementTest(TestCase):

    @mock.patch('analyticsclient.course.Course.recent_activity', mock.Mock(side_effect=mock_activity_data, autospec=True))
    def test_get_summary(self):
        student_engagement = StudentEngagement()
        summary = student_engagement.get_summary('this/course/id')

        # make sure that we get the time from "ANY"
        self.assertEqual(summary['interval_end'], 'this is a time 0')

        # make sure that activity counts all match up
        self.assertEqual(summary[AT.ANY], 0)
        self.assertEqual(summary[AT.ATTEMPTED_PROBLEM], 500)
        self.assertEqual(summary[AT.PLAYED_VIDEO], 1000)
        self.assertEqual(summary[AT.POSTED_FORUM], 1500)

class StudentEnrollmentTest(TestCase):

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(side_effect=mock_enrollment_data_empty, autospec=True))
    def test_get_summary_empty(self):
        student_enrollment = StudentEnrollment()
        summary = student_enrollment.get_summary('this/course/id')

        self.assertEqual(summary['date_end'], None)

        # make sure that the enrollment counts all match up
        self.assertEqual(summary['total_enrollment'], None)
        self.assertEqual(summary['enrollment_change_yesterday'], None)
        self.assertEqual(summary['enrollment_change_last_7_days'], None)
        self.assertEqual(summary['enrollment_change_last_30_days'], None)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(side_effect=mock_enrollment_data_full, autospec=True))
    def test_get_summary_full(self):
        student_enrollment = StudentEnrollment()
        summary = student_enrollment.get_summary('this/course/id')

        self.assertEqual(summary['date_end'], '2014-04-24')

        # make sure that the enrollment counts all match up
        self.assertEqual(summary['total_enrollment'], 0)
        self.assertEqual(summary['enrollment_change_yesterday'], -1)
        self.assertEqual(summary['enrollment_change_last_7_days'], -7)
        self.assertEqual(summary['enrollment_change_last_30_days'], -30)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(side_effect=mock_enrollment_data_full, autospec=True))
    def test_get_enrollment_trend(self):
        end_date = datetime.date(2014, 1, 15)
        days_past = 2

        student_enrollment = StudentEnrollment()
        enrollments = student_enrollment.get_enrollment_trend('this/course/id', end_date, days_past)

        # check the counts
        self.assertEqual(len(enrollments), days_past)
        self.assertEqual(enrollments[0]['count'], 1)
        self.assertEqual(enrollments[1]['count'], 0)

        # check the dates
        self.assertEqual(enrollments[0]['date'], '2014-01-14')
        self.assertEqual(enrollments[1]['date'], '2014-01-15')

    def test_calculate_trend_difference(self):
        student_enrollment = StudentEnrollment()

        counts = [10, 1]
        self.assertEqual(student_enrollment.calculate_trend_difference(counts), -9)

        counts = [1, 10]
        self.assertEqual(student_enrollment.calculate_trend_difference(counts), 9)

        counts = [1, 100, 7, 5, 20]
        self.assertEqual(student_enrollment.calculate_trend_difference(counts), 19)

        # check to make sure that we throw an exception when the array is too small
        counts = [0]
        self.assertRaises(ValueError, student_enrollment.calculate_trend_difference, counts)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(side_effect=mock_enrollment_data_full, autospec=True))
    def test_get_enrollment_change_full(self):
        student_enrollment = StudentEnrollment()
        end_date = datetime.date(2014, 1, 15)
        days_past = (5, 2)

        enrollment_changes = student_enrollment.get_enrollment_change('this/course/id', end_date, days_past)

        self.assertEqual(enrollment_changes[0], -4)
        self.assertEqual(enrollment_changes[1], -1)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(side_effect=mock_enrollment_data_empty, autospec=True))
    def test_get_enrollment_change_none(self):
        student_enrollment = StudentEnrollment()
        end_date = datetime.date(2014, 1, 15)
        days_past = (1, 6)

        enrollment_changes = student_enrollment.get_enrollment_change('this/course/id', end_date, days_past)

        self.assertEqual(enrollment_changes[0], None)
        self.assertEqual(enrollment_changes[1], None)

    def test_parse_enrollment_date(self):
        student_enrollment = StudentEnrollment()
        actual_date = student_enrollment.parse_enrollment_date({'date': '2014-04-24'})
        self.assertEqual(datetime.date(2014, 4, 24), actual_date)