from django.test import TestCase
from analytics_dashboard.backends import EdXOAuth2


class EdXOAuth2Tests(TestCase):
    def setUp(self):
        self.backend = EdXOAuth2()
        self.username = 'edx'
        self.response = {'username': self.username}

    def test_get_user_details(self):
        expected = {
            'username': self.username,
            'email': '',
            'fullname': '',
            'first_name': '',
            'last_name': ''
        }
        self.assertDictEqual(self.backend.get_user_details(self.response), expected)
