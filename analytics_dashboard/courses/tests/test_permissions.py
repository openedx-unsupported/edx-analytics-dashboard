import logging

from auth_backends.backends import EdXOpenIdConnect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
import mock
from testfixtures import LogCapture
from social.apps.django_app.default.models import UserSocialAuth
from django_dynamic_fixture import G

from courses.exceptions import UserNotAssociatedWithBackendError, InvalidAccessTokenError, \
    PermissionsRetrievalFailedError
from courses import permissions
from courses.tests.utils import set_empty_permissions

User = get_user_model()


class PermissionsTests(TestCase):
    def setUp(self):
        super(PermissionsTests, self).setUp()
        self.user = G(User)
        self.course_id = 'edX/DemoX/Demo_Course'

    def tearDown(self):
        super(PermissionsTests, self).tearDown()
        cache.clear()

    def test_set_user_course_permissions_invalid_arguments(self):
        """
        Verify that set_user_course_permissions requires both a User and course list
        """
        self.assertRaises(ValueError, permissions.set_user_course_permissions, None, None)
        self.assertRaises(ValueError, permissions.set_user_course_permissions, G(User), None)
        self.assertRaises(ValueError, permissions.set_user_course_permissions, None, [])

    def test_set_user_course_permissions(self):
        courses = []

        permissions.set_user_course_permissions(self.user, courses)
        permissions_key = 'course_permissions_{}'.format(self.user.pk)
        self.assertListEqual(cache.get(permissions_key), courses)

        update_key = 'course_permissions_updated_at_{}'.format(self.user.pk)
        last_updated = cache.get(update_key)
        self.assertIsNotNone(last_updated)

        courses = [self.course_id]
        permissions.set_user_course_permissions(self.user, courses)
        self.assertListEqual(cache.get(permissions_key), courses)
        self.assertGreater(cache.get(update_key), last_updated)
        self.assertTrue(permissions.user_can_view_course(self.user, self.course_id))

    def test_user_can_view_course(self):
        """
        Verify basic functionality of user_can_view_course.
        """

        # A user with no permissions should not be able to view the course.
        permissions.set_user_course_permissions(self.user, [])
        self.assertFalse(permissions.user_can_view_course(self.user, self.course_id))

        # The user should be able to view the course after the permissions have been set.
        permissions.set_user_course_permissions(self.user, [self.course_id])
        self.assertTrue(permissions.user_can_view_course(self.user, self.course_id))

    def test_superuser_can_view_course(self):
        """ Verify that superusers can view everything. """
        user = self.user
        user.is_superuser = True
        user.save()

        # With no permissions set, a superuser should still be able to view a course.
        permissions.set_user_course_permissions(user, [])
        self.assertTrue(permissions.user_can_view_course(user, self.course_id))

        # With permissions set, a superuser should be able to view a course
        # (although the individual permissions don't matter).
        permissions.set_user_course_permissions(user, [self.course_id])
        self.assertTrue(permissions.user_can_view_course(user, self.course_id))

    @mock.patch('courses.permissions.refresh_user_course_permissions', side_effect=set_empty_permissions)
    def test_user_can_view_course_refresh(self, mock_refresh):
        """
        Verify user_can_view_course refreshes permissions if they are not present in the cache.
        """

        # If permissions have not been set, or have expired, they should be refreshed
        self.assertFalse(permissions.user_can_view_course(self.user, self.course_id))
        mock_refresh.assert_called_with(self.user)
        self.assertFalse(permissions.user_can_view_course(self.user, self.course_id))

    @mock.patch('auth_backends.backends.EdXOpenIdConnect.get_json',
                mock.Mock(return_value={'staff_courses': ['edX/DemoX/Demo_Course']}))
    def test_refresh_user_course_permissions(self):
        """
        Verify course permissions are refreshed from the auth server.
        """
        courses = [self.course_id]

        # Make sure the cache is completely empty
        cache.clear()

        # If user is not associated with the edX OIDC backend, an exception should be raised.
        self.assertRaises(UserNotAssociatedWithBackendError, permissions.refresh_user_course_permissions, self.user)

        # Add backend association
        usa = G(UserSocialAuth, user=self.user, provider='edx-oidc', extra_data={})

        # An empty access token should raise an error
        self.assertRaises(InvalidAccessTokenError, permissions.refresh_user_course_permissions, self.user)

        # Set the access token
        usa.extra_data = {'access_token': '1234'}
        usa.save()

        # Refreshing the permissions should populate the cache and return the updated permissions
        actual = permissions.refresh_user_course_permissions(self.user)
        self.assertListEqual(list(actual), courses)

        # Verify the courses are stored in the cache
        permissions_key = 'course_permissions_{}'.format(self.user.pk)
        self.assertListEqual(cache.get(permissions_key), courses)

        # Verify the updated time is stored in the cache
        update_key = 'course_permissions_updated_at_{}'.format(self.user.pk)
        self.assertIsNotNone(cache.get(update_key))

        # Sanity check: verify the user can view the course
        self.assertTrue(permissions.user_can_view_course(self.user, self.course_id))

    @mock.patch('auth_backends.backends.EdXOpenIdConnect.get_json', mock.Mock(return_value={}))
    def test_refresh_user_course_permissions_with_missing_permissions(self):
        """
        If the authorization backend fails to return course permission data, a warning should be logged and the users
        should be assumed to have no course permissions.
        """

        G(UserSocialAuth, user=self.user, provider='edx-oidc', extra_data={'access_token': '1234'})

        # Make sure the cache is completely empty
        cache.clear()

        with LogCapture(level=logging.WARN) as l:
            # Refresh permissions
            actual = permissions.refresh_user_course_permissions(self.user)

            # Verify the correct permissions were returned
            self.assertListEqual(actual, [])

            # Verify the warning was logged
            l.check(('courses.permissions', 'WARNING',
                     'Authorization server did not return course permissions. Defaulting to no course access.'), )

    def test_revoke_user_permissions(self):
        courses = [self.course_id]
        permissions_key = 'course_permissions_{}'.format(self.user.pk)
        update_key = 'course_permissions_updated_at_{}'.format(self.user.pk)

        # Set permissions and verify cache is updated
        permissions.set_user_course_permissions(self.user, courses)
        self.assertListEqual(cache.get(permissions_key), courses)
        self.assertIsNotNone(cache.get(update_key))
        self.assertTrue(permissions.user_can_view_course(self.user, self.course_id))

        # Revoke permissions and verify cache cleared
        permissions.revoke_user_course_permissions(self.user)
        self.assertIsNone(cache.get(permissions_key))
        self.assertIsNone(cache.get(update_key))

    def test_get_user_course_permissions(self):
        courses = [self.course_id]
        with mock.patch('courses.permissions.refresh_user_course_permissions', return_value=courses):
            self.assertListEqual(permissions.get_user_course_permissions(self.user), courses)

        # Raise a PermissionsError if the backend is unavailable.
        G(UserSocialAuth, user=self.user, provider='edx-oidc', extra_data={'access_token': '1234'})
        with mock.patch('auth_backends.backends.EdXOpenIdConnect.get_json', side_effect=Exception):
            self.assertRaises(PermissionsRetrievalFailedError, permissions.get_user_course_permissions, self.user)

    def test_on_auth_complete(self):
        """ Verify the function receives the auth_complete_signal signal, and updates course permissions. """
        # No initial permissions
        permissions.set_user_course_permissions(self.user, [])
        self.assertFalse(permissions.user_can_view_course(self.user, self.course_id))

        # Permissions can be granted
        id_token = {claim: [self.course_id] for claim in settings.COURSE_PERMISSIONS_CLAIMS}
        EdXOpenIdConnect.auth_complete_signal.send(None, user=self.user, id_token=id_token)
        self.assertTrue(permissions.user_can_view_course(self.user, self.course_id))

        # Permissions can be revoked
        revoked_access_id_token = {claim: list() for claim in settings.COURSE_PERMISSIONS_CLAIMS}
        EdXOpenIdConnect.auth_complete_signal.send(None, user=self.user, id_token=revoked_access_id_token)
        self.assertFalse(permissions.user_can_view_course(self.user, self.course_id))
