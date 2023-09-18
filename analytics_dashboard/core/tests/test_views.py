import json
import logging

import unittest.mock as mock
from urllib.parse import quote
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import DatabaseError
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse, reverse_lazy
from django_dynamic_fixture import G
from testfixtures import LogCapture

from analytics_dashboard.core.views import OK, UNAVAILABLE
from analytics_dashboard.courses.permissions import (
    get_user_course_permissions,
    set_user_course_permissions,
    user_can_view_course,
)

User = get_user_model()


class UserTestCaseMixin:
    PASSWORD = 'password'

    def get_user(self):
        user = G(User)
        user.set_password('password')
        user.save()
        return user

    def login(self):
        assert self.client.login(username=self.user.username, password=self.PASSWORD), 'Login failed!'

    def get_latest_user(self):
        """
        Returns the most-recently created User.
        """

        return User.objects.latest('date_joined')

    def assertUserLoggedIn(self, user):
        """ Verifies that the specified user is logged in with the test client. """

        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def setUp(self):
        super().setUp()
        self.user = self.get_user()


class RedirectTestCaseMixin:
    def assertRedirectsNoFollow(self, response, expected_url, status_code=302, **querystringkwargs):
        if querystringkwargs:
            expected_url += '?{}'.format('&'.join('{}={}'.format(key, quote(value))
                                                  for (key, value) in querystringkwargs.items()))

        self.assertEqual(response['Location'], f'{expected_url}')
        self.assertEqual(response.status_code, status_code)


class ViewTests(TestCase):
    def verify_health_response(self, expected_status_code, overall_status, database_connection):
        """Verify that the health endpoint returns the expected response."""
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response['content-type'], 'application/json')
        expected = {
            'overall_status': overall_status,
            'detailed_status': {
                'database_connection': database_connection,
            }
        }
        self.assertDictEqual(json.loads(response.content.decode()), expected)

    def test_status(self):
        response = self.client.get(reverse('status'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    def test_healthy(self):
        with LogCapture(level=logging.ERROR) as log_capture:
            self.verify_health_response(
                expected_status_code=200, overall_status=OK, database_connection=OK
            )
            log_capture.check()

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    @mock.patch('django.db.backends.base.base.BaseDatabaseWrapper.cursor',
                mock.Mock(side_effect=DatabaseError('example error')))
    def test_health_database_outage(self):
        with LogCapture(level=logging.ERROR) as log_capture:
            self.verify_health_response(
                expected_status_code=503, overall_status=UNAVAILABLE, database_connection=UNAVAILABLE
            )
            log_capture.check(
                ('analytics_dashboard.core.views', 'ERROR', 'Insights database is not reachable: example error'),
                ('django.request', 'ERROR', 'Service Unavailable: /health/'),
            )


class LoginViewTests(RedirectTestCaseMixin, TestCase):
    def test_login_redirect(self):
        """
        The login page should redirect users to the OAuth2 provider's login page.
        """
        response = self.client.get(settings.LOGIN_URL)
        path = reverse('social:begin', args=['edx-oauth2'])
        self.assertRedirectsNoFollow(response, path, status_code=302)


class LogoutViewTests(RedirectTestCaseMixin, UserTestCaseMixin, TestCase):
    def test_logut_without_user(self):
        """
        Logging out without having been previously logged in should not raise an error
        """
        self.client.logout()

    def assertViewClearsPermissions(self, view_name):
        self.login()

        user = self.user
        course_id = 'edX/DemoX/Demo_Course'
        courses = [course_id]
        permissions_key = f'course_permissions_{user.pk}'
        update_key = f'course_permissions_updated_at_{user.pk}'

        # Set permissions and verify cache is updated
        set_user_course_permissions(user, courses)
        self.assertListEqual(cache.get(permissions_key), courses)
        self.assertIsNotNone(cache.get(update_key))
        self.assertTrue(user_can_view_course(user, course_id))

        # Logout by GETing the URL. self.client.logout() doesn't actually call this view.
        response = self.client.get(reverse(view_name))

        # Verify cache cleared
        self.assertIsNone(cache.get(permissions_key))
        self.assertIsNone(cache.get(update_key))

        return response

    def test_logout_clear_course_permissions(self):
        """
        Logging out should clear course permissions
        """
        self.assertViewClearsPermissions('logout')

    def test_logout_then_login(self):
        response = self.assertViewClearsPermissions('logout_then_login')
        self.assertRedirectsNoFollow(response, reverse('login'))


class AutoAuthTests(UserTestCaseMixin, TestCase):
    auto_auth_path = reverse_lazy('auto_auth')

    @override_settings(ENABLE_AUTO_AUTH=False)
    def test_setting_disabled(self):
        """
        When the ENABLE_AUTO_AUTH setting is set to False, the view should raise a 404.
        """
        response = self.client.get(self.auto_auth_path)
        self.assertEqual(response.status_code, 404)

    @override_settings(ENABLE_AUTO_AUTH=True)
    def test_setting_enabled(self):
        """
        When ENABLE_AUTO_AUTH is set to True, the view should create and authenticate a new User.
        """

        original_user_count = User.objects.count()
        response = self.client.get(self.auto_auth_path)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), original_user_count + 1)
        user = self.get_latest_user()
        self.assertUserLoggedIn(user)
        self.assertTrue(user.username.startswith(settings.AUTO_AUTH_USERNAME_PREFIX))

        self.assertListEqual(get_user_course_permissions(user), ['edX/DemoX/Demo_Course'])

    @override_settings(ENABLE_AUTO_AUTH=True, AUTO_AUTH_USERNAME_PREFIX=None)
    def test_prefix_invalid(self):
        original_user_count = User.objects.count()
        self.assertRaises(ValueError, self.client.get, self.auto_auth_path)
        self.assertEqual(User.objects.count(), original_user_count)
