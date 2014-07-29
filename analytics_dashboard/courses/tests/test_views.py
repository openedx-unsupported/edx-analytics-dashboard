import datetime
import json

import mock
from django.test import TestCase
from django.core.urlresolvers import reverse

import analyticsclient.activity_type as AT
from analyticsclient.exceptions import NotFoundError
from courses.tests.utils import get_mock_enrollment_data, get_mock_enrollment_location_data, \
    convert_list_of_dicts_to_csv


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
        expected = {
            'date': datetime.date(year=2014, month=1, day=31),
            'current_enrollment': 30,
            'enrollment_change_last_1_days': 1,
            'enrollment_change_last_7_days': 7,
            'enrollment_change_last_30_days': 30
        }
        self.assertDictEqual(context['summary'], expected)

        # make sure the trend is correct
        page_data = json.loads(context['page_data'])
        trend_data = page_data['enrollmentTrends']
        expected = enrollment_data
        self.assertListEqual(trend_data, expected)


class CourseViewTestMixin(object):
    viewname = None

    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.path = reverse(self.viewname, kwargs={'course_id': self.course_id})

    def assertResponseContentType(self, response, content_type):
        self.assertEqual(response['Content-Type'], content_type)

    def assertResponseFilename(self, response, filename):
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{0}"'.format(filename))

    def test_not_found(self):
        path = reverse(self.viewname, kwargs={'course_id': 'fakeOrg/soFake/Fake_Course'})
        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)


class CourseEnrollmentByCountryJSONViewTests(CourseViewTestMixin, TestCase):
    viewname = 'courses:json_enrollment_by_country'

    def convert_datum(self, datum):
        datum['date'] = '2014-01-01'
        datum['course_id'] = self.course_id
        datum['count'] = datum['value']
        datum['country'] = {
            'code': datum['country_code'],
            'name': datum['country_name']
        }

        del datum['country_code']
        del datum['country_name']
        del datum['value']

        return datum

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_response(self, mock_enrollment):
        data = get_mock_enrollment_location_data(self.course_id)
        mock_enrollment.return_value = data

        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'application/json')

        content = json.loads(response.content)

        # Check date
        expected = 'January 01, 2014'
        self.assertEqual(content['date'], expected)

        # Check data
        actual = [self.convert_datum(datum) for datum in content['data']]
        self.assertListEqual(actual, data)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(return_value=[]))
    def test_response_no_data(self):
        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'application/json')

        content = json.loads(response.content)

        # Check date
        self.assertIsNone(content['date'])

        # Check data
        self.assertListEqual(content['data'], [])


class CourseEnrollmentByCountryCSVViewTests(CourseViewTestMixin, TestCase):
    viewname = 'courses:csv_enrollment_by_country'

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_response(self, mock_enrollment):
        data = convert_list_of_dicts_to_csv(get_mock_enrollment_location_data(self.course_id))
        mock_enrollment.return_value = data

        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        filename = '{0}_enrollment_by_country.csv'.format(self.course_id)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, data)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_response_no_data(self, mock_enrollment):
        # Create an "empty" CSV that only has headers
        data = convert_list_of_dicts_to_csv([], ['count', 'country', 'course_id', 'date'])
        mock_enrollment.return_value = data

        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        filename = '{0}_enrollment_by_country.csv'.format(self.course_id)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, data)


class CourseEnrollmentCSVViewTests(CourseViewTestMixin, TestCase):
    viewname = 'courses:csv_enrollment'

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_response(self, mock_enrollment):
        data = convert_list_of_dicts_to_csv(get_mock_enrollment_data(self.course_id))
        mock_enrollment.return_value = data

        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        filename = '{0}_enrollment.csv'.format(self.course_id)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, data)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_response_no_data(self, mock_enrollment):
        # Create an "empty" CSV that only has headers
        data = convert_list_of_dicts_to_csv([], ['count', 'course_id', 'date'])
        mock_enrollment.return_value = data

        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        filename = '{0}_enrollment.csv'.format(self.course_id)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, data)
