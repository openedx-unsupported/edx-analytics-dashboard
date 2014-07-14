import mock

from django.test import Client
from django.test import TestCase
from django.core.urlresolvers import reverse

import analyticsclient.activity_type as AT
from analyticsclient.exceptions import ClientError

import courses.views as views

class StudentEngagementTestView(TestCase):

    def mock_summary_data(self):
        return {
            'interval_end': '2013-01-01T12:12:12Z',
            AT.ANY: 100,
            AT.ATTEMPTED_PROBLEM: 301,
            AT.PLAYED_VIDEO: 1000,
            AT.POSTED_FORUM: 0,
        }

    def mock_summary_error(self):
        raise ClientError()

    def test_get_formatted_date(self):
        actualDate = views.get_formatted_date('2013-01-01T12:12:12Z')
        self.assertEqual(actualDate, 'January 01, 2013')

    @mock.patch('courses.models.StudentEngagement.get_summary', mock.Mock(side_effect=mock_summary_data, autospec=True))
    def test_engagement_page_success(self):
        client = Client()
        response = client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))

        # make sure that we get a 200
        self.assertEqual(response.status_code, 200)

        # make sure the date is formatted correctly
        self.assertEqual(response.context['summary']['week_of_activity'], 'January 01, 2013')

        # check to make sure that we have tooltips
        self.assertTrue(len(response.context['tooltips']['all_activity_summary']) > 0)
        self.assertTrue(len(response.context['tooltips']['posted_forum_summary']) > 0)
        self.assertTrue(len(response.context['tooltips']['attempted_problem_summary']) > 0)
        self.assertTrue(len(response.context['tooltips']['played_video_summary']) > 0)

        # check page title
        self.assertEqual(response.context['page_title'], 'Engagement')

        # make sure the summary numbers are correct
        self.assertEqual(response.context['summary'][AT.ANY], 100)
        self.assertEqual(response.context['summary'][AT.ATTEMPTED_PROBLEM], 301)
        self.assertEqual(response.context['summary'][AT.PLAYED_VIDEO], 1000)
        self.assertEqual(response.context['summary'][AT.POSTED_FORUM], 0)

    @mock.patch('courses.models.StudentEngagement.get_summary', mock.Mock(side_effect=mock_summary_error, autospec=True))
    def test_engagement_page_fail(self):
        client = Client()
        response = client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))
        self.assertEqual(response.status_code, 404)

    def test_url_fail(self):
        client = Client()
        response = client.get('not_a_page_test')
        self.assertEqual(response.status_code, 404)
