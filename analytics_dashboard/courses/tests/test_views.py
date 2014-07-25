import json

import mock
from django.test import TestCase
from django.core.urlresolvers import reverse

import analyticsclient.activity_type as AT
from analyticsclient.exceptions import NotFoundError
from courses.tests.utils import get_mock_enrollment_data, get_mock_enrollment_summary


def mock_engagement_summary_data():
    return {
        'interval_end': '2013-01-01T12:12:12Z',
        AT.ANY: 100,
        AT.ATTEMPTED_PROBLEM: 301,
        AT.PLAYED_VIDEO: 1000,
        AT.POSTED_FORUM: 0,
    }


class StudentEngagementTestView(TestCase):
    @mock.patch('courses.presenters.CourseEngagementPresenter.get_summary',
                mock.Mock(return_value=mock_engagement_summary_data()))
    def test_engagement_page_success(self):
        response = self.client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))

        # make sure that we get a 200
        self.assertEqual(response.status_code, 200)

        # make sure the date is formatted correctly
        self.assertEqual(response.context['summary']['week_of_activity'], 'January 01, 2013')

        # check to make sure that we have tooltips
        self.assertEqual(response.context['tooltips']['all_activity_summary'], 'Students who initiated an action.')
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

    @mock.patch('courses.presenters.CourseEngagementPresenter.get_summary',
                mock.Mock(side_effect=NotFoundError, autospec=True))
    def test_engagement_page_fail(self):
        """
        The course engagement page should raise a 404 when there is an error accessing API data.
        """
        response = self.client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))
        self.assertEqual(response.status_code, 404)


class CourseEnrollmentViewTests(TestCase):
    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.path = reverse('courses:enrollment', kwargs={'course_id': self.course_id})

    @mock.patch('courses.presenters.CourseEnrollmentPresenter.get_summary', mock.Mock(side_effect=NotFoundError))
    def test_invalid_course(self):
        """ Return a 404 if the course is not found. """
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 404)

    @mock.patch('courses.presenters.CourseEnrollmentPresenter.get_data')
    def test_valid_course(self, mock_get_data):
        enrollment_data = get_mock_enrollment_data(self.course_id)
        mock_get_data.side_effect = [[enrollment_data[-1]], enrollment_data, enrollment_data]

        response = self.client.get(self.path)
        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        # check to make sure that we have tooltips
        expected = {
            'current_enrollment': 'Students enrolled in course.',
            'enrollment_change_last_1_days': 'Change in enrollment for the last full day (00:00-23:59 UTC).',
            'enrollment_change_last_7_days': 'Change in enrollment during the last 7 days (through 23:59 UTC).',
            'enrollment_change_last_30_days': 'Change in enrollment during the last 30 days (through 23:59 UTC).'
        }
        self.assertDictEqual(context['tooltips'], expected)

        # check page title
        self.assertEqual(context['page_title'], 'Enrollment')

        # make sure the summary numbers are correct
        self.assertDictEqual(context['summary'], get_mock_enrollment_summary())

        # make sure the trend is correct
        page_data = json.loads(context['page_data'])
        trend_data = page_data['enrollmentTrends']
        expected = enrollment_data
        self.assertListEqual(trend_data, expected)
