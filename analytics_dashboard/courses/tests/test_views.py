import mock
import json

from django.test import TestCase
from django.core.urlresolvers import reverse

import analyticsclient.activity_type as AT
from analyticsclient.exceptions import NotFoundError

def mock_enrollment_summary_data(self):
    return {
        'date_end': '2013-01-01',
        'total_enrollment': 100,
        'enrollment_change_yesterday': 31301,
        'enrollment_change_last_7_days': -1000,
        'enrollment_change_last_30_days': None,
    }

def mock_enrollment_trend(self, course_id, end_date=None, days_past=1):
    return [
        {'count': 10, 'date': '2013-01-01'},
        {'count': 9823, 'date': '2013-01-02'}
    ]

def mock_engagement_summary_data(self):
    return {
        'interval_end': '2013-01-01T12:12:12Z',
        AT.ANY: 100,
        AT.ATTEMPTED_PROBLEM: 301,
        AT.PLAYED_VIDEO: 1000,
        AT.POSTED_FORUM: 0,
    }

class StudentEngagementTestView(TestCase):

    @mock.patch('courses.presenters.StudentEngagement.get_summary', mock.Mock(side_effect=mock_engagement_summary_data, autospec=True))
    def test_engagement_page_success(self):
        response = self.client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))

        # make sure that we get a 200
        self.assertEqual(response.status_code, 200)

        # make sure the date is formatted correctly
        self.assertEqual(response.context['summary']['week_of_activity'], 'January 01, 2013')

        # check to make sure that we have tooltips
        self.assertEqual(response.context['tooltips']['all_activity_summary'],
                         'Students who initiated an action.')
        self.assertEqual(response.context['tooltips']['posted_forum_summary'],
                         'Students who created a post, responded to a post, or made a comment in any discussion.')
        self.assertEqual(response.context['tooltips']['attempted_problem_summary'],
                         'Students who answered any question.')
        self.assertEqual(response.context['tooltips']['played_video_summary'],
                         'Students who started watching any video.')

        # check page title
        self.assertEqual(response.context['page_title'], 'Engagement')

        # make sure the summary numbers are correct
        self.assertEqual(response.context['summary'][AT.ANY], 100)
        self.assertEqual(response.context['summary'][AT.ATTEMPTED_PROBLEM], 301)
        self.assertEqual(response.context['summary'][AT.PLAYED_VIDEO], 1000)
        self.assertEqual(response.context['summary'][AT.POSTED_FORUM], 0)

    @mock.patch('courses.presenters.StudentEngagement.get_summary', mock.Mock(side_effect=NotFoundError, autospec=True))
    def test_engagement_page_fail(self):
        """
        The course engagement page should raise a 404 when there is an error accessing API data.
        """
        response = self.client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))
        self.assertEqual(response.status_code, 404)

class StudentEnrollmentTestView(TestCase):

    @mock.patch('courses.presenters.StudentEnrollment.get_summary', mock.Mock(side_effect=mock_enrollment_summary_data, autospec=True))
    @mock.patch('courses.presenters.StudentEnrollment.get_enrollment_trend', mock.Mock(side_effect=mock_enrollment_trend, autospec=True))
    def test_enrollment_page_success(self):
        response = self.client.get(reverse('courses:enrollment', kwargs={'course_id': 'this/is/course'}))

        # make sure that we get a 200
        self.assertEqual(response.status_code, 200)

        # make sure the date is formatted correctly
        self.assertEqual(response.context['summary']['last_update'], 'January 01, 2013')

        # check to make sure that we have tooltips
        self.assertEqual(response.context['tooltips']['total_enrollment'],
                         'Students enrolled in course.')
        self.assertEqual(response.context['tooltips']['enrollment_change_yesterday'],
                         'Change in enrollment for the past day (through yesterday).')
        self.assertEqual(response.context['tooltips']['enrollment_change_last_7_days'],
                         'Change in enrollment during the past week (7 days ending yesterday).')
        self.assertEqual(response.context['tooltips']['enrollment_change_last_30_days'],
                         'Change in enrollment over the past month (30 days ending yesterday).')

        # check page title
        self.assertEqual(response.context['page_title'], 'Enrollment')

        # make sure the summary numbers are correct
        self.assertEqual(response.context['summary']['total_enrollment'], '100')
        self.assertEqual(response.context['summary']['enrollment_change_yesterday'], '+31,301')
        self.assertEqual(response.context['summary']['enrollment_change_last_7_days'], '-1,000')
        self.assertEqual(response.context['summary']['enrollment_change_last_30_days'], 'n/a')

        # make sure the trend is correct
        page_data = json.loads(response.context['page_data'])
        trend_data = page_data['enrollmentTrends']
        self.assertEqual(len(trend_data), 2)
        self.assertEqual(trend_data[0]['date'], '2013-01-01')
        self.assertEqual(trend_data[1]['date'], '2013-01-02')

        # check the counts
        self.assertEqual(trend_data[0]['count'], 10)
        self.assertEqual(trend_data[1]['count'], 9823)

    @mock.patch('courses.presenters.StudentEnrollment.get_summary', mock.Mock(side_effect=NotFoundError, autospec=True))
    def test_enrollment_not_found_error_page_fail(self):
        """
        The course engagement page should raise a 404 when there is an error accessing API data.
        """
        response = self.client.get(reverse('courses:enrollment', kwargs={'course_id': 'this/is/course'}))
        self.assertEqual(response.status_code, 404)
