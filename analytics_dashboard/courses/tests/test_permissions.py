import unittest.mock as mock
import ddt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from django_dynamic_fixture import G
from edx_django_utils.cache import TieredCache
from social_django.models import UserSocialAuth

from analytics_dashboard.courses import permissions
from analytics_dashboard.courses.exceptions import PermissionsRetrievalFailedError

User = get_user_model()


@ddt.ddt
class PermissionsTests(TestCase):
    TEST_ACCESS_TOKEN = 'test-access-token'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TieredCache.dangerous_clear_all_tiers()
        cache.clear()

    def setUp(self):
        super().setUp()
        self.user = G(User)
        self.course_id = 'edX/DemoX/Demo_Course'
        self.new_course_id = 'edX/DemoX/New_Demo_Course'

    def tearDown(self):
        super().tearDown()
        TieredCache.dangerous_clear_all_tiers()
        cache.clear()

    def test_get_user_tracking_id_from_oauth2_provider(self):
        expected_tracking_id = 56789
        G(UserSocialAuth, user=self.user, provider='edx-oauth2', extra_data={'user_id': expected_tracking_id})
        actual_tracking_id = permissions.get_user_tracking_id(self.user)
        self.assertEqual(actual_tracking_id, expected_tracking_id)
        # make sure tracking ID is cached
        self.assertEqual(cache.get(f'user_tracking_id_{self.user.id}'), expected_tracking_id)

    def test_user_tracking_settings_with_no_user(self):
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
        permissions_key = f'course_permissions_{self.user.pk}'
        self.assertListEqual(cache.get(permissions_key), courses)

        update_key = f'course_permissions_updated_at_{self.user.pk}'
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

    @mock.patch('analytics_dashboard.courses.permissions.OAuthAPIClient')
    def test_get_user_course_permissions(self, mock_client):
        """
        Verify course permissions are retrieved and cached, even when paged.
        """
        page_size = 5
        course_ids = [str(x) for x in range(page_size * 2)]
        expected_calls = self._setup_mock_course_ids_responses_and_expects(mock_client, course_ids, page_size=page_size)

        # Check permissions
        self.assertCountEqual(permissions.get_user_course_permissions(self.user), course_ids)
        self.assertCountEqual(expected_calls, mock_client.mock_calls)

        # Check newly permitted course is not returned because the earlier permissions are cached
        mock_client.reset_mock()
        self._setup_mock_course_ids_responses_and_expects(mock_client, [self.new_course_id])
        self.assertCountEqual(permissions.get_user_course_permissions(self.user), course_ids)
        self.assertFalse(mock_client.mock_calls)

        # Check original permissions again
        mock_client.reset_mock()
        self.assertCountEqual(permissions.get_user_course_permissions(self.user), course_ids)
        self.assertFalse(mock_client.mock_calls)

    @mock.patch('analytics_dashboard.courses.permissions.OAuthAPIClient')
    def test_get_user_course_permissions_after_permission_timeout(self, mock_client):
        """
        Verify course permissions are retrieved multiple times when the permission cache times out.
        """
        self._setup_mock_course_ids_responses_and_expects(mock_client, [self.course_id])

        with override_settings(COURSE_PERMISSIONS_TIMEOUT=0):
            # Check permissions
            expected_courses = [self.course_id]
            self.assertEqual(permissions.get_user_course_permissions(self.user), expected_courses)

            # Check permission succeeds for a newly permitted course because the earlier permission timed out
            self._setup_mock_course_ids_responses_and_expects(mock_client, [self.new_course_id])
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

    @mock.patch('analytics_dashboard.courses.permissions.OAuthAPIClient')
    def test_user_can_view_course_with_permissions_failure(self, mock_client):
        """
        Verify proper error is raised when the permissions api request fails.
        """
        mock_client.return_value.get.side_effect = Exception

        self.assertRaises(
            PermissionsRetrievalFailedError, permissions.user_can_view_course, self.user, 'test-course-id'
        )

    def test_revoke_user_permissions(self):
        courses = [self.course_id]
        permissions_key = f'course_permissions_{self.user.pk}'
        update_key = f'course_permissions_updated_at_{self.user.pk}'

        # Set permissions and verify cache is updated
        permissions.set_user_course_permissions(self.user, courses)
        self.assertListEqual(cache.get(permissions_key), courses)
        self.assertIsNotNone(cache.get(update_key))
        self.assertTrue(permissions.user_can_view_course(self.user, self.course_id))

        # Revoke permissions and verify cache cleared
        permissions.revoke_user_course_permissions(self.user)
        self.assertIsNone(cache.get(permissions_key))
        self.assertIsNone(cache.get(update_key))

    def _setup_mock_course_ids_responses_and_expects(self, mock_client, course_ids, page_size=100):
        """ Sets up mock client calls for course_ids endpoint and returns the expected calls to be made. """
        paged_responses = []
        course_id_pages = [course_ids[x:x + page_size] for x in range(0, len(course_ids), page_size)]
        for page, course_ids_for_page in enumerate(course_id_pages, start=1):
            if page == len(course_id_pages):
                next_page_url = None
            else:
                # This mock url is not perfect, but good enough
                next_page_url = 'http://course-api-host/course_ids?page={}'.format(page + 1)
            response = {
                'pagination': {
                    'next': next_page_url
                },
                'results': course_ids_for_page
            }
            paged_responses.append(response)

        # adds mock response for each page
        mock_client.return_value.get.return_value.json.side_effect = paged_responses

        # return expected calls for each page
        return self._get_expected_permissions_client_calls(len(course_id_pages))

    def _get_expected_permissions_client_calls(self, expected_pages):
        expected_calls = [
            # OAuthAPIClient auth request
            mock.call(
                settings.BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL,
                settings.BACKEND_SERVICE_EDX_OAUTH2_KEY,
                settings.BACKEND_SERVICE_EDX_OAUTH2_SECRET,
            )
        ]
        for page in range(1, expected_pages + 1):
            expected_calls += [
                mock.call().get(
                    settings.COURSE_API_URL + 'course_ids/',
                    params={
                        'page': page,
                        'page_size': 1000,
                        'role': 'staff',
                        'username': self.user.username
                    },
                    timeout=(3.05, 55)
                ),
                mock.call().get().json(),
                mock.call().get().raise_for_status(),
            ]
        return expected_calls
