import uuid

from ddt import data, ddt, unpack

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import TestCase

from core.utils import CourseStructureApiClient, delete_auto_auth_users, sanitize_cache_key


User = get_user_model()


class UtilsTests(TestCase):
    def test_delete_auto_auth_users(self):
        # Create an auto-auth user
        username = password = settings.AUTO_AUTH_USERNAME_PREFIX + uuid.uuid4().hex[0:20]
        User.objects.create_user(username, password=password)
        user_count = User.objects.count()

        # Call a command that should remove all auto-auth users
        delete_auto_auth_users()

        # Verify the user has been removed
        self.assertEqual(User.objects.count(), user_count - 1)

    @override_settings(AUTO_AUTH_USERNAME_PREFIX=None)
    def test_delete_auto_auth_users_empty_prefix(self):
        # Create a user without the (empty) prefix
        username = password = uuid.uuid4().hex[0:20]
        User.objects.create_user(username, password=password)
        user_count = User.objects.count()

        # The deletion command should raise an error
        self.assertRaises(ValueError, delete_auto_auth_users)

        # No users should have been deleted
        self.assertEqual(User.objects.count(), user_count)

    def test_sanitize_cache_key(self):
        keys = ['', ' ', 'I am a key. AMA!']

        for key in keys:
            sanitized = sanitize_cache_key(key)
            self.assertLess(len(sanitized), 250)

            # TODO Add a proper assertion to ensure all control characters are removed.
            self.assertNotIn(' ', sanitized)


@ddt
class CourseStructureApiClientTests(TestCase):
    """
    Tests the CourseStructureApiClient wrapper class.
    """
    @data((None, None), ('http://example.com/', None), (None, 'arbitrary_access_token'))
    @unpack
    def test_required_args(self, url, access_token):
        with self.assertRaises(ValueError):
            CourseStructureApiClient(url, access_token)

    def test_default_timeout(self):
        client = CourseStructureApiClient('http://example.com/', 'arbitrary_access_token')
        # pylint: disable=protected-access
        self.assertEqual(client._store['session'].timeout, settings.LMS_DEFAULT_TIMEOUT)

    def test_explicit_timeout(self):
        client = CourseStructureApiClient('http://example.com/', 'arbitrary_access_token', timeout=2.5)
        # pylint: disable=protected-access
        self.assertEqual(client._store['session'].timeout, 2.5)
