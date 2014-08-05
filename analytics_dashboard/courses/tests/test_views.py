import datetime
import json
import analyticsclient
import mock

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
import analyticsclient.activity_type as AT
from analyticsclient.exceptions import NotFoundError

from analytics_dashboard.tests.test_views import RedirectTestCaseMixin, UserTestCaseMixin
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


class CourseViewTestMixin(RedirectTestCaseMixin, UserTestCaseMixin):
    viewname = None

    def setUp(self):
        super(CourseViewTestMixin, self).setUp()
        self.course_id = 'edX/DemoX/Demo_Course'
        self.path = reverse(self.viewname, kwargs={'course_id': self.course_id})
        self.login()

    def assertResponseContentType(self, response, content_type):
        self.assertEqual(response['Content-Type'], content_type)

    def assertResponseFilename(self, response, filename):
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{0}"'.format(filename))

    def test_not_found(self):
        path = reverse(self.viewname, kwargs={'course_id': 'fakeOrg/soFake/Fake_Course'})
        response = self.client.get(path, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_authentication(self):
        """
        Users must be logged in to view course data.
        """

        # Authenticated users should go to the course page
        response = self.client.get(self.path, follow=True)
        self.assertEqual(response.status_code, 200)

        # Unauthenticated users should be redirected to the login page
        self.client.logout()
        response = self.client.get(self.path)
        self.assertRedirectsNoFollow(response, settings.LOGIN_URL, next=self.path)


class CourseEnrollmentViewTestMixin(CourseViewTestMixin):
    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(side_effect=NotFoundError))
    def test_not_found(self):
        super(CourseEnrollmentViewTestMixin, self).test_not_found()

    def test_authentication(self):
        with mock.patch.object(analyticsclient.course.Course, 'enrollment',
                               return_value=get_mock_enrollment_data(self.course_id)):
            super(CourseEnrollmentViewTestMixin, self).test_authentication()


class CourseEngagementViewTests(CourseViewTestMixin, TestCase):
    viewname = 'courses:engagement'

    @mock.patch('courses.presenters.CourseEngagementPresenter.get_summary',
                mock.Mock(return_value=mock_engagement_summary_data()))
    def test_engagement_page_success(self):
        response = self.client.get(self.path)

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
    def test_not_found(self):
        super(CourseEngagementViewTests, self).test_not_found()

    @mock.patch('courses.presenters.CourseEngagementPresenter.get_summary',
                mock.Mock(return_value=mock_engagement_summary_data()))
    def test_authentication(self):
        super(CourseEngagementViewTests, self).test_authentication()


class CourseEnrollmentViewTests(CourseEnrollmentViewTestMixin, TestCase):
    viewname = 'courses:enrollment'

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
        trend_data = page_data['course']['enrollmentTrends']
        expected = enrollment_data
        self.assertListEqual(trend_data, expected)


class CourseEnrollmentByCountryJSONViewTests(CourseEnrollmentViewTestMixin, TestCase):
    viewname = 'courses:json_enrollment_by_country'

    def convert_datum(self, datum):
        '''
        Converts the country data returned from the JSON endpoint to the format
        returned by the client API.  This is used to compare the two outputs.
        '''
        datum['date'] = '2014-01-01'
        datum['course_id'] = self.course_id
        datum['country'] = {
            'alpha3': datum['countryCode'],
            'name': datum['countryName']
        }

        del datum['countryCode']
        del datum['countryName']

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

    def test_authentication(self):
        with mock.patch.object(analyticsclient.course.Course, 'enrollment',
                               return_value=get_mock_enrollment_location_data(self.course_id)):
            # Call CourseEnrollmentViewTestMixin.test_authentication in order
            # to bypass the Mock in CourseEnrollmentViewTestMixin.test_authentication.
            super(CourseEnrollmentViewTestMixin, self).test_authentication()  # pylint: disable=bad-super-call


class CourseEnrollmentByCountryCSVViewTests(CourseEnrollmentViewTestMixin, TestCase):
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


class CourseEnrollmentCSVViewTests(CourseEnrollmentViewTestMixin, TestCase):
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

        self.client.login(username=self.user.username, password=self.PASSWORD)
        response = self.client.get(self.path)

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        filename = '{0}_enrollment.csv'.format(self.course_id)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, data)


class CourseHomeViewTests(CourseEnrollmentViewTestMixin, TestCase):
    """
    Course homepage

    We do not actually have a course homepage, so redirect to the enrollment page.
    """
    viewname = 'courses:home'

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_redirect(self, mock_enrollment):
        mock_enrollment.return_value = get_mock_enrollment_data(self.course_id)

        response = self.client.get(self.path)
        expected_url = reverse('courses:enrollment', kwargs={'course_id': self.course_id})
        self.assertRedirectsNoFollow(response, expected_url)
