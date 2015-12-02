from calendar import timegm
import json
import logging
import datetime
from testfixtures import LogCapture

import httpretty
import jwt
import mock

from django.core.cache import cache
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.test import TestCase
from django.test.utils import override_settings
from django_dynamic_fixture import G

from analyticsclient.exceptions import TimeoutError
from social.exceptions import AuthException
from social.utils import parse_qs

from auth_backends.backends import EdXOpenIdConnect
from core.views import OK, UNAVAILABLE
from courses.permissions import set_user_course_permissions, user_can_view_course, get_user_course_permissions


User = get_user_model()


class UserTestCaseMixin(object):
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

        self.assertEqual(self.client.session['_auth_user_id'], user.pk)

    def setUp(self):
        super(UserTestCaseMixin, self).setUp()
        self.user = self.get_user()


class RedirectTestCaseMixin(object):
    def assertRedirectsNoFollow(self, response, expected_url, status_code=302, **querystringkwargs):
        if querystringkwargs:
            expected_url += '?{}'.format('&'.join('%s=%s' % (key, value) for (key, value) in querystringkwargs.items()))

        self.assertEqual(response['Location'], 'http://testserver{}'.format(expected_url))
        self.assertEqual(response.status_code, status_code)


class ViewTests(TestCase):
    def verify_health_response(self, expected_status_code, overall_status, database_connection, analytics_api):
        """Verify that the health endpoint returns the expected response."""
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response['content-type'], 'application/json')
        expected = {
            u'overall_status': overall_status,
            u'detailed_status': {
                u'database_connection': database_connection,
                u'analytics_api': analytics_api
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    def test_status(self):
        response = self.client.get(reverse('status'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    def test_healthy(self):
        with LogCapture(level=logging.ERROR) as l:
            self.verify_health_response(
                expected_status_code=200, overall_status=OK, database_connection=OK, analytics_api=OK
            )
            l.check()

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    @mock.patch('django.db.backends.BaseDatabaseWrapper.cursor', mock.Mock(side_effect=DatabaseError('example error')))
    def test_health_database_outage(self):
        with LogCapture(level=logging.ERROR) as l:
            self.verify_health_response(
                expected_status_code=503, overall_status=UNAVAILABLE, database_connection=UNAVAILABLE, analytics_api=OK
            )
            l.check(('analytics_dashboard.core.views', 'ERROR', 'Insights database is not reachable: example error'))

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=False))
    def test_health_analytics_api_unhealthy(self):
        with LogCapture(level=logging.ERROR) as l:
            self.verify_health_response(
                expected_status_code=503, overall_status=UNAVAILABLE, database_connection=OK, analytics_api=UNAVAILABLE
            )
            l.check(('analytics_dashboard.core.views', 'ERROR', 'Analytics API health check failed from dashboard'))

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(side_effect=TimeoutError('example error')))
    def test_health_analytics_api_unreachable(self):
        with LogCapture(level=logging.ERROR) as l:
            self.verify_health_response(
                expected_status_code=503, overall_status=UNAVAILABLE, database_connection=OK, analytics_api=UNAVAILABLE
            )
            l.check((
                'analytics_dashboard.core.views',
                'ERROR',
                'Analytics API health check timed out from dashboard: example error'
            ))

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=False))
    @mock.patch('django.db.backends.BaseDatabaseWrapper.cursor', mock.Mock(side_effect=DatabaseError('example error')))
    def test_health_both_unavailable(self):
        with LogCapture(level=logging.ERROR) as l:
            self.verify_health_response(
                expected_status_code=503, overall_status=UNAVAILABLE,
                database_connection=UNAVAILABLE, analytics_api=UNAVAILABLE
            )
            l.check(
                (
                    'analytics_dashboard.core.views',
                    'ERROR',
                    'Insights database is not reachable: example error'
                ),
                (
                    'analytics_dashboard.core.views',
                    'ERROR',
                    'Analytics API health check failed from dashboard'
                )
            )


class LoginViewTests(RedirectTestCaseMixin, TestCase):
    def test_login_redirect(self):
        """
        The login page should redirect users to the OAuth2 provider's login page.
        """
        response = self.client.get(settings.LOGIN_URL)
        path = reverse('social:begin', args=['edx-oidc'])
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
        permissions_key = 'course_permissions_{}'.format(user.pk)
        update_key = 'course_permissions_updated_at_{}'.format(user.pk)

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


@override_settings(SOCIAL_AUTH_EDX_OIDC_KEY='123',
                   SOCIAL_AUTH_EDX_OIDC_SECRET='abc',
                   SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY='abc')
class OpenIdConnectTests(UserTestCaseMixin, RedirectTestCaseMixin, TestCase):
    DEFAULT_USERNAME = 'edx'
    backend_name = 'edx-oidc'
    backend_class = EdXOpenIdConnect
    user_is_administrator = False

    def setUp(self):
        super(OpenIdConnectTests, self).setUp()
        self.oauth2_init_path = reverse('social:begin', args=[self.backend_name])

    def _access_token_body(self, request, _url, headers, username):
        nonce = parse_qs(request.body).get('nonce')
        body = json.dumps(self.get_access_token_response(nonce, username))
        return 200, headers, body

    # pylint: disable=unused-argument
    def get_access_token_response(self, nonce, username):
        client_secret = settings.SOCIAL_AUTH_EDX_OIDC_SECRET
        access_token = {
            'access_token': '12345',
            'refresh_token': 'abcde',
            'expires_in': 900,
            'preferred_username': username,
            'id_token': jwt.encode(self.get_id_token(nonce, username), client_secret).decode('utf-8')
        }
        return access_token

    def get_id_token(self, nonce, username):
        client_key = settings.SOCIAL_AUTH_EDX_OIDC_KEY
        now = datetime.datetime.utcnow()
        expiration_datetime = now + datetime.timedelta(seconds=30)
        issue_datetime = now

        id_token = {
            'iss': EdXOpenIdConnect.ID_TOKEN_ISSUER,
            'nonce': nonce,
            'aud': client_key,
            'azp': client_key,
            'exp': timegm(expiration_datetime.utctimetuple()),
            'iat': timegm(issue_datetime.utctimetuple()),
            'sub': '1234',
            'preferred_username': username,
            'email': 'edx@example.org',
            'name': 'Ed Xavier',
            'given_name': 'Ed',
            'family_name': 'Xavier',
            'locale': 'en_US',
            'administrator': self.user_is_administrator
        }

        return id_token

    @httpretty.activate
    def _check_oauth2_handshake(self, username=DEFAULT_USERNAME, failure=False):
        """ Performs an OAuth2 handshake to login a user.

        Arguments:
            username -- Username of the user to login (or create if one does not exist)
            failure  -- Determines if handshake should fail
        """

        # Generate an OAuth2 request
        response = self.client.get(self.oauth2_init_path)
        self.assertEqual(response.status_code, 302)
        state = self.client.session['{}_state'.format(self.backend_name)]

        # Mock the access token POST body
        httpretty.register_uri(httpretty.POST, self.backend_class.ACCESS_TOKEN_URL,
                               body=lambda request, url, headers: self._access_token_body(request, url, headers,
                                                                                          username))

        # Send the response to this application's OAuth2 consumer URL
        oauth2_complete_path = '{0}?state={1}'.format(reverse('social:complete', args=[self.backend_name]), state)

        if failure:
            oauth2_complete_path += '&error=access_denied'
            self.assertRaises(AuthException, self.client.get, oauth2_complete_path)
        else:
            response = self.client.get(oauth2_complete_path)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], 'http://testserver{}'.format(settings.LOGIN_REDIRECT_URL))

    def test_new_user(self):
        """
        A new user should be created if the username from the OAuth2 provider is not linked to an existing account.
        """

        original_user_count = User.objects.count()

        self._check_oauth2_handshake()

        # Verify new user created
        self.assertEqual(User.objects.count(), original_user_count + 1)
        user = self.get_latest_user()
        self.assertEqual(user.username, self.DEFAULT_USERNAME)

        self.assertUserLoggedIn(user)

    def test_existing_user(self):
        """
        Verify system logs in a user (and does not create a new account) when the username from the OAuth2 provider
        matches an existing account in the system.
        """
        user = self.user

        original_user_count = User.objects.count()

        self._check_oauth2_handshake(user.username)

        # Verify no new users created
        self.assertEqual(User.objects.count(), original_user_count)

        self.assertUserLoggedIn(user)

    def test_access_denied(self):
        self._check_oauth2_handshake(failure=True)

    def test_user_details(self):
        # Create a new user
        self.test_new_user()
        user = self.get_latest_user()

        # Validate the user's details
        self.assertEqual(user.username, 'edx')
        self.assertEqual(user.email, 'edx@example.org')
        self.assertEqual(user.first_name, 'Ed')
        self.assertEqual(user.last_name, 'Xavier')
        self.assertEqual(user.language, 'en-us')

    def test_administrator(self):
        # Create an administrator via OAuth2
        self.user_is_administrator = True
        self._check_oauth2_handshake()

        user = self.get_latest_user()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


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
