import uuid

from copy import deepcopy
from ddt import ddt
from mock import call, MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from core.utils import (CourseStructureApiClient, delete_auto_auth_users, sanitize_cache_key, translate_dict_values,
                        remove_keys, Message)


User = get_user_model()


class UtilsTests(TestCase):
    def setUp(self):
        self.acceptance_tests_mock = MagicMock()
        self.acceptance_tests_mock.SOAPBOX_INACTIVE_MESSAGE = 'inactive'
        self.acceptance_tests_mock.SOAPBOX_GLOBAL_MESSAGE = 'global'
        self.acceptance_tests_mock.SOAPBOX_SINGLE_PAGE_MESSAGE = 'single-page'
        self.acceptance_tests_mock.SOAPBOX_SINGLE_PAGE_VIEW = 'view'
        modules = {
            'acceptance_tests': self.acceptance_tests_mock,
        }
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from core.utils import create_fake_soapbox_messages, delete_fake_soapbox_messages
        self.create_messages = create_fake_soapbox_messages
        self.delete_messages = delete_fake_soapbox_messages

    def tearDown(self):
        self.module_patcher.stop()

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

    def test_remove_keys(self):
        dict_of_dicts = {
            'foo': {
                'bar': {
                    'baz': 1,
                    'fizz': 2
                }
            },
            'flat': 0
        }
        flat_dict = {
            'foo': 1,
            'bar': 2,
            'baz': 3
        }

        flat_dict_no_foo = flat_dict.copy()
        del flat_dict_no_foo['foo']
        self.assertDictEqual(remove_keys(flat_dict, ('foo',)), flat_dict_no_foo)

        dict_of_dicts_no_fizz = deepcopy(dict_of_dicts)
        del dict_of_dicts_no_fizz['foo']['bar']['fizz']
        self.assertDictEqual(remove_keys(dict_of_dicts, {'foo': {'bar': ('fizz',)}}), dict_of_dicts_no_fizz)

        del dict_of_dicts_no_fizz['flat']
        self.assertDictEqual(remove_keys(dict_of_dicts, {'foo': {'bar': ('fizz',)}, '': ('flat',)}),
                             dict_of_dicts_no_fizz)

    @patch.object(Message, 'objects')
    def test_create_fake_soapbox_messages(self, objects_mock):
        self.create_messages()
        calls = [
            call(message=self.acceptance_tests_mock.SOAPBOX_GLOBAL_MESSAGE, is_active=True, is_global=True),
            call(message=self.acceptance_tests_mock.SOAPBOX_SINGLE_PAGE_MESSAGE, is_active=True, is_global=False,
                 url=self.acceptance_tests_mock.SOAPBOX_SINGLE_PAGE_VIEW),
            call(message=self.acceptance_tests_mock.SOAPBOX_INACTIVE_MESSAGE, is_active=False, is_global=True),
        ]
        objects_mock.get_or_create.assert_has_calls(calls)

    @patch.object(Message, 'objects')
    def test_delete_fake_soapbox_messages(self, objects_mock):
        self.delete_messages()
        calls = [
            call(message=self.acceptance_tests_mock.SOAPBOX_GLOBAL_MESSAGE, is_active=True, is_global=True),
            call().delete(),
            call(message=self.acceptance_tests_mock.SOAPBOX_SINGLE_PAGE_MESSAGE, is_active=True, is_global=False,
                 url=self.acceptance_tests_mock.SOAPBOX_SINGLE_PAGE_VIEW),
            call().delete(),
            call(message=self.acceptance_tests_mock.SOAPBOX_INACTIVE_MESSAGE, is_active=False, is_global=True),
            call().delete(),
        ]
        objects_mock.get.assert_has_calls(calls)


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
