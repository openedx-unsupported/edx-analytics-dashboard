from ddt import ddt, data
from django.core.urlresolvers import reverse
import mock
from django.core.cache import cache
from django.conf import settings

from analytics_dashboard.tests.test_views import RedirectTestCaseMixin, UserTestCaseMixin
from courses.permissions import set_user_course_permissions, revoke_user_course_permissions
from courses.tests.utils import set_empty_permissions


DEMO_COURSE_ID = 'course-v1:edX+DemoX+Demo_2014'
DEPRECATED_DEMO_COURSE_ID = 'edX/DemoX/Demo_Course'


class PermissionsTestMixin(object):
    def tearDown(self):
        super(PermissionsTestMixin, self).tearDown()
        cache.clear()

    def grant_permission(self, user, *courses):
        set_user_course_permissions(user, courses)

    def revoke_permissions(self, user):
        revoke_user_course_permissions(user)


class MockApiTestMixin(object):
    api_method = None

    def get_mock_data(self, course_id):
        raise NotImplementedError


# pylint: disable=not-callable,abstract-method
@ddt
class AuthTestMixin(MockApiTestMixin, PermissionsTestMixin, RedirectTestCaseMixin, UserTestCaseMixin):
    def setUp(self):
        super(AuthTestMixin, self).setUp()
        self.grant_permission(self.user, DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
        self.login()

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_authentication(self, course_id):
        """
        Users must be logged in to view the page.
        """

        if self.api_method:
            with mock.patch(self.api_method, return_value=self.get_mock_data(course_id)):
                # Authenticated users should go to the course page
                self.login()
                response = self.client.get(self.path(course_id), follow=True)
                self.assertEqual(response.status_code, 200)

                # Unauthenticated users should be redirected to the login page
                self.client.logout()
                response = self.client.get(self.path(course_id))
                self.assertRedirectsNoFollow(response, settings.LOGIN_URL, next=self.path(course_id))

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    @mock.patch('courses.permissions.refresh_user_course_permissions', mock.Mock(side_effect=set_empty_permissions))
    def test_authorization(self, course_id):
        """
        Users must be authorized to view a course in order to view the course pages.
        """

        if self.api_method:
            with mock.patch(self.api_method, return_value=self.get_mock_data(course_id)):
                # Authorized users should be able to view the page
                self.grant_permission(self.user, course_id)
                response = self.client.get(self.path(course_id), follow=True)
                self.assertEqual(response.status_code, 200)

                # Unauthorized users should be redirected to the 403 page
                self.revoke_permissions(self.user)
                response = self.client.get(self.path(course_id), follow=True)
                self.assertEqual(response.status_code, 403)


# pylint: disable=abstract-method
class ViewTestMixin(AuthTestMixin):
    viewname = None

    def path(self, course_id=None):
        kwargs = {}
        if course_id:
            kwargs['course_id'] = course_id

        return reverse(self.viewname, kwargs=kwargs)
