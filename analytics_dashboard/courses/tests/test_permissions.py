import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django_dynamic_fixture import G
import mock
from testfixtures import LogCapture

from courses.exceptions import UserNotAssociatedWithBackendError, InvalidAccessToken
from courses.permissions import set_user_course_permissions, user_can_view_course, refresh_user_course_permissions, \
    revoke_user_course_permissions
from social.apps.django_app.default.models import UserSocialAuth
from courses.tests.utils import set_empty_permissions

User = get_user_model()


class PermissionsTests(TestCase):
    def tearDown(self):
        super(PermissionsTests, self).tearDown()
        cache.clear()

    def test_set_user_course_permissions_invalid_arguments(self):
        """
        Verify that set_user_course_permissions requires both a User and course list
        """
        self.assertRaises(ValueError, set_user_course_permissions, None, None)
        self.assertRaises(ValueError, set_user_course_permissions, G(User), None)
        self.assertRaises(ValueError, set_user_course_permissions, None, [])

    def test_set_user_course_permissions(self):
        user = G(User)
        courses = []

        set_user_course_permissions(user, courses)
        permissions_key = 'course_permissions_{}'.format(user.pk)
        self.assertListEqual(cache.get(permissions_key), courses)

        update_key = 'course_permissions_updated_at_{}'.format(user.pk)
        last_updated = cache.get(update_key)
        self.assertIsNotNone(last_updated)

        course_id = 'edX/DemoX/Demo_Course'
        courses = [course_id]
        set_user_course_permissions(user, courses)
        self.assertListEqual(cache.get(permissions_key), courses)
        self.assertGreater(cache.get(update_key), last_updated)
        self.assertTrue(user_can_view_course(user, course_id))

    def test_user_can_view_course(self):
        """
        Verify basic functionality of user_can_view_course.
        """
        user = G(User)
        course_id = 'edX/DemoX/Demo_Course'

        # A user with no permissions should not be able to view the course.
        set_user_course_permissions(user, [])
        self.assertFalse(user_can_view_course(user, course_id))

        # The user should be able to view the course after the permissions have been set.
        set_user_course_permissions(user, [course_id])
        self.assertTrue(user_can_view_course(user, course_id))

    @mock.patch('courses.permissions.refresh_user_course_permissions', side_effect=set_empty_permissions)
    def test_user_can_view_course_refresh(self, mock_refresh):
        """
        Verify user_can_view_course refreshes permissions if they are not present in the cache.
        """

        user = G(User)
        course_id = 'edX/DemoX/Demo_Course'

        # If permissions have not been set, or have expired, they should be refreshed
        self.assertFalse(user_can_view_course(user, course_id))
        mock_refresh.assert_called_with(user)
        self.assertFalse(user_can_view_course(user, course_id))

    @mock.patch('analytics_dashboard.backends.EdXOpenIdConnect.get_user_permissions',
                mock.Mock(return_value={'courses': ['edX/DemoX/Demo_Course']}))
    def test_refresh_user_course_permissions(self):
        """
        Verify course permissions are refreshed from the auth server.
        """
        user = G(User)
        course_id = 'edX/DemoX/Demo_Course'
        courses = [course_id]

        # Make sure the cache is completely empty
        cache.clear()

        # If user is not associated with the edX OIDC backend, an exception should be raised.
        self.assertRaises(UserNotAssociatedWithBackendError, refresh_user_course_permissions, user)

        # Add backend association
        usa = G(UserSocialAuth, user=user, provider='edx-oidc', extra_data={})

        # An empty access token should raise an error
        self.assertRaises(InvalidAccessToken, refresh_user_course_permissions, user)

        # Set the access token
        usa.extra_data = {'access_token': '1234'}
        usa.save()

        # Refreshing the permissions should populate the cache and return the updated permissions
        actual = refresh_user_course_permissions(user)
        self.assertListEqual(actual, courses)

        # Verify the courses are stored in the cache
        permissions_key = 'course_permissions_{}'.format(user.pk)
        self.assertListEqual(cache.get(permissions_key), courses)

        # Verify the updated time is stored in the cache
        update_key = 'course_permissions_updated_at_{}'.format(user.pk)
        self.assertIsNotNone(cache.get(update_key))

        # Sanity check: verify the user can view the course
        self.assertTrue(user_can_view_course(user, course_id))

    @mock.patch('analytics_dashboard.backends.EdXOpenIdConnect.get_user_permissions',
                mock.Mock(return_value={}))
    def test_refresh_user_course_permissions_with_missing_permissions(self):
        """
        If the authorization backend fails to return course permission data, a warning should be logged and the users
        should be assumed to have no course permissions.
        """

        user = G(User)
        G(UserSocialAuth, user=user, provider='edx-oidc', extra_data={'access_token': '1234'})

        # Make sure the cache is completely empty
        cache.clear()

        with LogCapture(level=logging.WARN) as l:
            # Refresh permissions
            actual = refresh_user_course_permissions(user)

            # Verify the correct permissions were returned
            self.assertListEqual(actual, [])

            # Verify the warning was logged
            l.check(('courses.permissions', 'WARNING',
                     'Authorization server did not return course permissions. Defaulting to no course access.'), )

    def test_revoke_user_permissions(self):
        user = G(User)
        course_id = 'edX/DemoX/Demo_Course'
        courses = [course_id]
        permissions_key = 'course_permissions_{}'.format(user.pk)
        update_key = 'course_permissions_updated_at_{}'.format(user.pk)

        # Set permissions and verify cache is updated
        set_user_course_permissions(user, courses)
        self.assertListEqual(cache.get(permissions_key), courses)
        self.assertIsNotNone(cache.get(update_key))
        self.assertTrue(user_can_view_course(user, course_id))

        # Revoke permissions and verify cache cleared
        revoke_user_course_permissions(user)
        self.assertIsNone(cache.get(permissions_key))
        self.assertIsNone(cache.get(update_key))
