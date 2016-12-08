from ddt import ddt, data
from django.core.urlresolvers import reverse
from django.test import TestCase
import mock

from analyticsclient.exceptions import NotFoundError
from courses.tests.test_views import ViewTestMixin
from courses.tests.utils import (
    convert_list_of_dicts_to_csv,
    CourseSamples,
    get_mock_api_course_activity,
    get_mock_api_enrollment_age_data,
    get_mock_api_enrollment_data,
    get_mock_api_enrollment_education_data,
    get_mock_api_enrollment_gender_data,
    get_mock_api_enrollment_geography_data,
)


@ddt
# pylint: disable=abstract-method
class CourseCSVTestMixin(ViewTestMixin):
    client = None
    column_headings = None
    base_file_name = None

    def assertIsValidCSV(self, course_id, csv_data):
        response = self.client.get(self.path(course_id=course_id))

        # Check content type
        self.assertResponseContentType(response, 'text/csv')

        # Check filename
        csv_prefix = u'edX-DemoX-Demo_2014' if course_id == CourseSamples.DEMO_COURSE_ID else u'edX-DemoX-Demo_Course'
        filename = '{0}--{1}.csv'.format(csv_prefix, self.base_file_name)
        self.assertResponseFilename(response, filename)

        # Check data
        self.assertEqual(response.content, csv_data)

    def assertResponseContentType(self, response, content_type):
        self.assertEqual(response['Content-Type'], content_type)

    def assertResponseFilename(self, response, filename):
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{0}"'.format(filename))

    def _test_csv(self, course_id, csv_data):
        with mock.patch(self.api_method, return_value=csv_data):
            self.assertIsValidCSV(course_id, csv_data)

    @data(CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID)
    def test_response_no_data(self, course_id):
        # Create an "empty" CSV that only has headers
        csv_data = convert_list_of_dicts_to_csv([], self.column_headings)
        self._test_csv(course_id, csv_data)

    @data(CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID)
    def test_response(self, course_id):
        csv_data = self.get_mock_data(course_id)
        csv_data = convert_list_of_dicts_to_csv(csv_data)
        self._test_csv(course_id, csv_data)

    def test_404(self):
        course_id = 'fakeOrg/soFake/Fake_Course'
        self.grant_permission(self.user, course_id)
        path = reverse(self.viewname, kwargs={'course_id': course_id})

        with mock.patch(self.api_method, side_effect=NotFoundError):
            response = self.client.get(path, follow=True)
            self.assertEqual(response.status_code, 404)


class CourseEnrollmentByCountryCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:enrollment_geography'
    column_headings = ['count', 'country', 'course_id', 'date']
    base_file_name = 'enrollment-location'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_geography_data(course_id)


class CourseEnrollmentCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:enrollment'
    column_headings = ['count', 'course_id', 'date']
    base_file_name = 'enrollment'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_data(course_id)


class CourseEnrollmentModeCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:enrollment'
    column_headings = ['count', 'course_id', 'date', 'audit', 'honor', 'professional', 'verified']
    base_file_name = 'enrollment'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_data(course_id)


class CourseEnrollmentDemographicsByAgeCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:enrollment_demographics_age'
    column_headings = ['birth_year', 'count', 'course_id', 'created', 'date']
    base_file_name = 'enrollment-by-birth-year'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_age_data(course_id)


class CourseEnrollmentDemographicsByEducationCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:enrollment_demographics_education'
    column_headings = ['count', 'course_id', 'created', 'date', 'education_level.name', 'education_level.short_name']
    base_file_name = 'enrollment-by-education'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_education_data(course_id)


class CourseEnrollmentByDemographicsGenderCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:enrollment_demographics_gender'
    column_headings = ['count', 'course_id', 'created', 'date', 'gender']
    base_file_name = 'enrollment-by-gender'
    api_method = 'analyticsclient.course.Course.enrollment'

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_gender_data(course_id)


class CourseEngagementActivityTrendCSVViewTests(CourseCSVTestMixin, TestCase):
    viewname = 'courses:csv:engagement_activity_trend'
    column_headings = ['any', 'attempted_problem', 'course_id', 'interval_end', 'interval_start',
                       'played_video', 'posted_forum']
    base_file_name = 'engagement-activity'
    api_method = 'analyticsclient.course.Course.activity'

    def get_mock_data(self, course_id):
        return get_mock_api_course_activity(course_id)


@ddt
class PerformanceProblemResponseCSVTests(ViewTestMixin, TestCase):
    viewname = 'courses:csv:performance_problem_responses'
    follow = False  # Inherited methods test_authentication() and test_authorization() should not follow redirects
    success_status = 302
    course_id = 'course-v1:Test+ing+This'
    api_method = 'analyticsclient.course.Course.reports'
    api_response = {
        "course_id": "Test_ing_This",
        "report_name": "problem_response",
        "download_url": "https://bucket.s3.amazonaws.com/Test_ing_This_problem_response.csv?Signature=...",
        "last_modified": "2016-08-12T043411",
        "file_size": 3419,
        "expiration_date": "2016-08-12T233704",
    }
    api_response_minimal = {
        "course_id": "Test_ing_This",
        "report_name": "problem_response",
        "download_url": "https://bucket.s3.amazonaws.com/Test_ing_This_problem_response.csv?Signature=...",
    }

    def get_mock_data(self, course_id):
        return self.api_response.copy()

    @data(api_response, api_response_minimal)
    def test_working_download_redirect(self, api_response):
        """ A user with permission should be able to download a report """
        self.grant_permission(self.user, self.course_id)

        with mock.patch(self.api_method, return_value=api_response.copy()):
            response = self.client.get(self.path(course_id=self.course_id))
            self.assertEqual(response.status_code, self.success_status)
            self.assertEqual(response['Location'], self.api_response["download_url"])

    def test_no_data(self):
        """ Expect a 404 when the report for this course is not available from the API """
        self.grant_permission(self.user, self.course_id)
        with mock.patch(self.api_method, side_effect=NotFoundError):
            response = self.client.get(self.path(course_id=self.course_id))
            self.assertEqual(response.status_code, 404)
