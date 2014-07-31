from django.contrib.auth import get_user_model
from django.test import TestCase
from django_dynamic_fixture import G
from analytics_dashboard.pipeline import get_user_if_exists

User = get_user_model()


class PipelineTests(TestCase):
    def test_get_user_if_exists(self):
        username = 'edx'
        details = {'username': username}

        # If no user exists, return an empty dict
        actual = get_user_if_exists(None, details)
        self.assertDictEqual(actual, {})

        # If user exists, return dict with user and any additional information
        user = G(User, username=username)
        actual = get_user_if_exists(None, details)
        self.assertDictEqual(actual, {'is_new': False, 'user': user})

        # If user passed to function, just return the additional information
        actual = get_user_if_exists(None, details, user=user)
        self.assertDictEqual(actual, {'is_new': False})
