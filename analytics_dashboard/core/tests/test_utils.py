import uuid

from copy import deepcopy
from ddt import ddt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from core.utils import CourseStructureApiClient, delete_auto_auth_users, sanitize_cache_key, translate_dict_values


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

    def test_translate_dict_values(self):
        list_of_dicts = [
            {'foo': '1', 'bar': '2', 'baz': '2'},
            {'foo': '4', 'bar': '2', 'baz': '3'},
        ]
        expected = deepcopy(list_of_dicts)
        for a_dict in expected:
            a_dict['translated_foo'] = _(a_dict['foo'])

        self.assertTrue(translate_dict_values(list_of_dicts, ('foo',)))

        self.assertListEqual(expected, list_of_dicts)

        self.assertFalse(translate_dict_values(list_of_dicts, ('foo',)))

        with self.assertRaises(KeyError):
            translate_dict_values(list_of_dicts, ('bad',))


@ddt
class CourseStructureApiClientTests(TestCase):
    """
    Tests the CourseStructureApiClient wrapper class.
    """

    def test_default_timeout(self):
        client = CourseStructureApiClient('http://example.com/', 'arbitrary_access_token')
        # pylint: disable=protected-access
        self.assertEqual(client._store['session'].timeout, settings.LMS_DEFAULT_TIMEOUT)

    def test_explicit_timeout(self):
        client = CourseStructureApiClient('http://example.com/', 'arbitrary_access_token', timeout=2.5)
        # pylint: disable=protected-access
        self.assertEqual(client._store['session'].timeout, 2.5)
