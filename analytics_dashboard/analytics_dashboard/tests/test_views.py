import json
from django.core.cache import cache
from django.test.utils import override_settings
import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django_dynamic_fixture import G
from django.core.urlresolvers import reverse
from django.test import TestCase

from analyticsclient.exceptions import ClientError

from analytics_dashboard.backends import EdXOAuth2
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
    def assertUnhealthyAPI(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        expected = {
            u'overall_status': u'UNAVAILABLE',
            u'detailed_status': {
                u'database_connection': u'OK',
                u'analytics_api': u'UNAVAILABLE'
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    def test_status(self):
        response = self.client.get(reverse('status'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    def test_health(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        expected = {
            u'overall_status': u'OK',
            u'detailed_status': {
                u'database_connection': u'OK',
                u'analytics_api': u'OK'
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    @mock.patch('django.db.backends.BaseDatabaseWrapper.cursor', mock.Mock(side_effect=DatabaseError))
    def test_health_database_outage(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        expected = {
            u'overall_status': u'UNAVAILABLE',
            u'detailed_status': {
                u'database_connection': u'UNAVAILABLE',
                u'analytics_api': u'OK'
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=False))
    def test_health_analytics_api_unhealthy(self):
        self.assertUnhealthyAPI()

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(side_effect=ClientError))
    def test_health_analytics_api_unreachable(self):
        self.assertUnhealthyAPI()


class LoginViewTests(RedirectTestCaseMixin, TestCase):
    def test_login_redirect(self):
        """
        The login page should redirect users to the OAuth provider's login page.
        """
        response = self.client.get(settings.LOGIN_URL)
        path = reverse('social:begin', args=['edx-oidc'])
        self.assertRedirectsNoFollow(response, path, status_code=302)


class LogoutViewTests(UserTestCaseMixin, TestCase):
    def test_logut_without_user(self):
        """
        Logging out without having been previously logged in should not raise an error
        """
        self.client.logout()

    def test_logout_clear_course_permissions(self):
        """
        Logging out should clear course permissions
        """

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
        self.client.get(reverse('logout'))

        # Verify cache cleared
        self.assertIsNone(cache.get(permissions_key))
        self.assertIsNone(cache.get(update_key))


class OAuthTests(UserTestCaseMixin, RedirectTestCaseMixin, TestCase):
    DEFAULT_USERNAME = 'edx'
    backend_name = 'edx-oauth2'

    def setUp(self):
        super(OAuthTests, self).setUp()
        self.oauth_init_path = reverse('social:begin', args=[self.backend_name])

    def _check_oauth_handshake(self, username=DEFAULT_USERNAME, failure=False):
        """ Performs an OAuth handshake to login a user.

        Arguments:
            username -- Username of the user to login (or create if one does not exist)
            failure  -- Determines if handshake should fail
        """

        # Generate an OAuth request
        response = self.client.get(self.oauth_init_path)
        self.assertEqual(response.status_code, 302)
        state = self.client.session['{}_state'.format(self.backend_name)]

        # Generate an OAuth response
        token_response = {
            'access_token': '12345',
            'refresh_token': 'abcde',
            'expires_in': 900,
            'preferred_username': username
        }

        with mock.patch.object(EdXOAuth2, 'request_access_token', return_value=token_response):
            # Send the response to this application's OAuth consumer URL
            oauth_complete_path = '{0}?state={1}'.format(reverse('social:complete', args=[self.backend_name]), state)

            if failure:
                oauth_complete_path += '&error=access_denied'

            response = self.client.get(oauth_complete_path)
            self.assertEqual(response.status_code, 302)

            redirect_path = settings.SOCIAL_AUTH_LOGIN_ERROR_URL if failure else settings.LOGIN_REDIRECT_URL
            self.assertEqual(response['Location'], 'http://testserver{}'.format(redirect_path))

    def test_oauth_new_user(self):
        """
        A new user should be created if the username from the OAuth provider is not linked to an existing account.
        """

        original_user_count = User.objects.count()

        self._check_oauth_handshake()

        # Verify new user created
        self.assertEqual(User.objects.count(), original_user_count + 1)
        user = self.get_latest_user()
        self.assertEqual(user.username, self.DEFAULT_USERNAME)

        self.assertUserLoggedIn(user)

    def test_oauth_existing_user(self):
        """
        Verify system logs in a user (and does not create a new account) when the username from the OAuth provider
        matches an existing account in the system.
        """
        user = self.user

        original_user_count = User.objects.count()

        self._check_oauth_handshake(user.username)

        # Verify no new users created
        self.assertEqual(User.objects.count(), original_user_count)

        self.assertUserLoggedIn(user)

    def test_oauth_access_denied(self):
        self._check_oauth_handshake(failure=True)


class AutoAuthTests(UserTestCaseMixin, TestCase):
    @override_settings(ENABLE_AUTO_AUTH=False)
    def test_setting_disabled(self):
        """
        When the ENABLE_AUTO_AUTH setting is set to False, the view should raise a 404.
        """
        response = self.client.get(reverse('auto_auth'))
        self.assertEqual(response.status_code, 404)

    @override_settings(ENABLE_AUTO_AUTH=True)
    def test_setting_enabled(self):
        """
        When ENABLE_AUTO_AUTH is set to True, the view should create and authenticate a new User.
        """

        original_user_count = User.objects.count()
        response = self.client.get(reverse('auto_auth'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), original_user_count + 1)
        user = self.get_latest_user()
        self.assertUserLoggedIn(user)
        self.assertTrue(user.username.startswith('AUTO_AUTH_'))

        self.assertListEqual(get_user_course_permissions(user), ['edX/DemoX/Demo_Course'])
