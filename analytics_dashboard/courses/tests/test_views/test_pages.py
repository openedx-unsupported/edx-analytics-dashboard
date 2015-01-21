# pylint: disable=abstract-method

from ddt import data, ddt
import httpretty
import mock
from django.test import TestCase

from courses.tests.test_views import ViewTestMixin, CourseViewTestMixin, DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID, \
    CourseAPIMixin

from courses.exceptions import PermissionsRetrievalFailedError
from courses.tests.test_middleware import MiddlewareAssertionMixin


@ddt
class CourseHomeViewTests(CourseViewTestMixin, TestCase):
    viewname = 'courses:home'

    def assertViewIsValid(self, course_id):
        response = self.client.get(self.path(course_id=course_id))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['page_title'], 'Course Home')
        self.assertValidCourseName(course_id, response.context)

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_missing_data(self, course_id):
        self.skipTest('The course homepage does not check for the existence of a course.')


class CourseIndexViewTests(CourseAPIMixin, ViewTestMixin, MiddlewareAssertionMixin, TestCase):
    viewname = 'courses:index'

    def setUp(self):
        super(CourseIndexViewTests, self).setUp()
        self.grant_permission(self.user, DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
        self.courses = self._create_course_list(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)

    def assertCourseListEquals(self, courses):
        response = self.client.get(self.path())
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['courses'], courses)

    def _create_course_list(self, *course_keys, **kwargs):
        with_name = kwargs.get('with_name', False)
        return [{'key': key, 'name': 'Test ' + key if with_name else None} for key in course_keys]

    def test_get(self):
        """ If the user is authorized, the view should return a list of all accessible courses. """
        self.assertCourseListEquals(self.courses)

    def test_get_with_mixed_permissions(self):
        """ If user only has permission to one course, course list should only display the one course. """
        self.revoke_permissions(self.user)
        self.grant_permission(self.user, DEMO_COURSE_ID)
        courses = self._create_course_list(DEMO_COURSE_ID)
        self.assertCourseListEquals(courses)

    def test_get_unauthorized(self):
        """ The view should raise an error if the user has no course permissions. """
        self.grant_permission(self.user)
        response = self.client.get(self.path())
        self.assertEqual(response.status_code, 403)

    @httpretty.activate
    def test_get_with_course_api(self):
        """ Verify that the view properly retrieves data from the course API. """
        self.toggle_switch('enable_course_api', True)
        self.mock_course_list()
        courses = self._create_course_list(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID, with_name=True)
        self.assertCourseListEquals(courses)

        # Test with mixed permissions
        self.revoke_permissions(self.user)
        self.grant_permission(self.user, DEMO_COURSE_ID)
        courses = self._create_course_list(DEMO_COURSE_ID, with_name=True)
        self.assertCourseListEquals(courses)

    @mock.patch('courses.permissions.get_user_course_permissions',
                mock.Mock(side_effect=PermissionsRetrievalFailedError))
    def test_get_with_permissions_error(self):
        response = self.client.get(self.path())
        self.assertIsPermissionsRetrievalFailedResponse(response)
