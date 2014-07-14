import mock

from django.test import Client
from django.test import TestCase
from django.core.urlresolvers import reverse

from analyticsclient.exceptions import ClientError

import views as views

class StudentEngagementTestView(TestCase):

    def mock_summary_data(self):
        return {
            'interval_end': '2013-01-01T12:12:12Z'
        }

    def mock_summary_error(self):
        raise ClientError()

    def test_date_formatter(self):
        actualDate = views.get_formatted_date('2013-01-01T12:12:12Z')
        self.assertEqual(actualDate, 'January 01, 2013')

    @mock.patch('courses.models.StudentEngagement.get_summary', mock.Mock(side_effect=mock_summary_data, autospec=True))
    def test_engagement_page_success(self):
        client = Client()
        response = client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))

        # make sure that we get a 200
        self.assertEqual(response.status_code, 200)

        # check to see if we have data for the page
        self.assertEqual(response.context[-1]['summary']['week_of_activity'], 'January 01, 2013')
        self.assertTrue('tooltips' in response.context)
        self.assertTrue('page_title' in response.context)
        self.assertTrue('summary' in response.context)

    @mock.patch('courses.models.StudentEngagement.get_summary', mock.Mock(side_effect=mock_summary_error, autospec=True))
    def test_engagement_page_fail(self):
        client = Client()
        response = client.get(reverse('courses:engagement', kwargs={'course_id': 'this/is/course'}))
        self.assertEqual(response.status_code, 404)
