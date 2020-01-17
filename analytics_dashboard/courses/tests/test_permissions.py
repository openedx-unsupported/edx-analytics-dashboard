from datetime import datetime, timedelta
import mock

import ddt
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from social_django.models import UserSocialAuth
from django_dynamic_fixture import G

from courses import permissions
from courses.exceptions import (
    AccessTokenRetrievalFailedError,
    PermissionsRetrievalFailedError,
)

User = get_user_model()


@ddt.ddt
class PermissionsTests(TestCase):
    TEST_ACCESS_TOKEN = 'test-access-token'

    @classmethod
    def setUpClass(cls):
        super(PermissionsTests, cls).setUpClass()
        cache.clear()

    def setUp(self):
        super(PermissionsTests, self).setUp()
        self.user = G(User)
        self.course_id = 'edX/DemoX/Demo_Course'
        self.new_course_id = 'edX/DemoX/New_Demo_Course'

    def tearDown(self):
        super(PermissionsTests, self).tearDown()
        cache.clear()

    def test_get_user_tracking_id_from_oauth2_provider(self):
        expected_tracking_id = 56789
        G(UserSocialAuth, user=self.user, provider='edx-oauth2', extra_data={'user_id': expected_tracking_id})
        actual_tracking_id = permissions.get_user_tracking_id(self.user)
        self.assertEqual(actual_tracking_id, expected_tracking_id)
        # make sure tracking ID is cached
        self.assertEqual(cache.get('user_tracking_id_{}'.format(self.user.id)), expected_tracking_id)

    @override_settings(USER_TRACKING_CLAIM='user_tracking_id')
    @mock.patch('auth_backends.backends.EdXOpenIdConnect.get_json',
                mock.Mock(return_value={'user_tracking_id': 56789}))
    def test_get_user_tracking_id_from_deprecated_oidc_provider(self):
        G(UserSocialAuth, user=self.user, provider='edx-oidc', extra_data={'access_token': '1234'})
        actual_tracking_id = permissions.get_user_tracking_id(self.user)
        expected_tracking_id = 56789
        self.assertEqual(actual_tracking_id, expected_tracking_id)
        # make sure tracking ID is cached
        self.assertEqual(cache.get('user_tracking_id_{}'.format(self.user.id)), expected_tracking_id)

    @ddt.data('user_tracking_id', None)
    def test_user_tracking_settings_with_no_user(self, user_tracking_claim_setting):
        with override_settings(USER_TRACKING_CLAIM=user_tracking_claim_setting):
            tracking_id = permissions.get_user_tracking_id(self.user)
            self.assertEqual(tracking_id, None)

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
        permissions.set_user_course_permissions(self.user, [])
        self.assertTrue(permissions.user_can_view_course(user, self.course_id))

        # With permissions set, a superuser should be able to view a course
        # (although the individual permissions don't matter).
        permissions.set_user_course_permissions(self.user, [self.course_id])
        self.assertTrue(permissions.user_can_view_course(user, self.course_id))

    @mock.patch('courses.permissions.EdxRestApiClient')
    def test_get_user_course_permissions(self, mock_client):
        """
        Verify course permissions are retrieved and cached.
        """
        self._setup_mock_client_courses_response(mock_client, [self.course_id])
        hour_expiration_datetime = datetime.utcnow() + timedelta(hours=1)
        mock_client.get_and_cache_jwt_oauth_access_token.return_value = (
            self.TEST_ACCESS_TOKEN, hour_expiration_datetime
        )

        # Check permissions
        expected_courses = [self.course_id]
        self.assertEqual(permissions.get_user_course_permissions(self.user), expected_courses)
        self.assertTrue(mock_client.mock_calls)

        # Check newly permitted course is not returned because the earlier permissions are cached
        mock_client.reset_mock()
        self._setup_mock_client_courses_response(mock_client, [self.new_course_id])
        self.assertEqual(permissions.get_user_course_permissions(self.user), expected_courses)
        self.assertFalse(mock_client.mock_calls)

        # Check original permissions again
        mock_client.reset_mock()
        expected_courses = [self.course_id]
        self.assertEqual(permissions.get_user_course_permissions(self.user), expected_courses)
        self.assertFalse(mock_client.mock_calls)

    @mock.patch('courses.permissions.EdxRestApiClient')
    def test_get_user_course_permissions_after_permission_timeout(self, mock_client):
        """
        Verify course permissions are retrieved multiple times when the permission cache times out.
        """
        self._setup_mock_client_courses_response(mock_client, [self.course_id])
        hour_expiration_datetime = datetime.utcnow() + timedelta(hours=1)
        mock_client.get_and_cache_jwt_oauth_access_token.return_value = (
            self.TEST_ACCESS_TOKEN, hour_expiration_datetime
        )

        with override_settings(COURSE_PERMISSIONS_TIMEOUT=0):
            # Check permissions
            expected_courses = [self.course_id]
            self.assertEqual(permissions.get_user_course_permissions(self.user), expected_courses)

            # Check permission succeeds for a newly permitted course because the earlier permission timed out
            self._setup_mock_client_courses_response(mock_client, [self.new_course_id])
            expected_courses = [self.new_course_id]
            self.assertEqual(permissions.get_user_course_permissions(self.user), expected_courses)

    def _get_access_token_client_calls(self):
        return [
            mock.call.get_oauth_access_token(
                'http://provider-host/oauth2/access_token',
                'test_backend_oauth2_key',
                'test_backend_oauth2_secret',
                token_type='jwt'
            ),
        ]

    def _get_permissions_client_calls(self):
        return [
            mock.call('http://course-api-host/courses', jwt=self.TEST_ACCESS_TOKEN),
            mock.call().courses(),
            mock.call().courses().get(page=1, page_size=100, role='staff', username=self.user.username),
        ]

    @mock.patch('courses.permissions.EdxRestApiClient')
    def test_user_can_view_course_with_access_token_failure(self, mock_client):
        """
        Verify proper error is raised when the access token request fails.
        """
        mock_client.get_and_cache_jwt_oauth_access_token.side_effect = Exception

        self.assertRaises(
            AccessTokenRetrievalFailedError, permissions.user_can_view_course, self.user, 'test-course-id'
        )

    @mock.patch('courses.permissions.EdxRestApiClient')
    def test_user_can_view_course_with_permissions_failure(self, mock_client):
        """
        Verify proper error is raised when the permissions api request fails.
        """
        mock_client.return_value.courses.side_effect = Exception
        expires_now_datetime = datetime.utcnow()
        mock_client.get_and_cache_jwt_oauth_access_token.return_value = (self.TEST_ACCESS_TOKEN, expires_now_datetime)

        self.assertRaises(
            PermissionsRetrievalFailedError, permissions.user_can_view_course, self.user, 'test-course-id'
        )

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

    def _setup_mock_client_courses_response(self, mock_client, course_ids):
        courses = [{'id': course_id} for course_id in course_ids]
        response = {
            'pagination': {
                'next': None
            },
            'results': courses
        }
        mock_client.return_value.courses.return_value.get.return_value = response
