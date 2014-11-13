import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import TestCase

from analytics_dashboard.utils import delete_auto_auth_users


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
