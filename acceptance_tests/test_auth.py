from unittest import skipUnless

from bok_choy.web_app_test import WebAppTest

from acceptance_tests import ENABLE_OAUTH_TESTS
from acceptance_tests.mixins import LoginMixin
from acceptance_tests.pages import LoginPage


@skipUnless(ENABLE_OAUTH_TESTS, 'OAuth tests are not enabled.')
class OAuth2FlowTests(LoginMixin, WebAppTest):
    def setUp(self):
        """
        Instantiate the page objects.
        """
        super(OAuth2FlowTests, self).setUp()

        self.insights_login_page = LoginPage(self.browser)

    def test_login(self):
        self.login_with_lms()

        # Visit login URL and get redirected
        self.insights_login_page.visit()

        # User should arrive at course index page (or access denied page, if no permissions)
        # Splitting this out into two separate tests would require two separate sets of credentials. That is
        # feasible, but somewhat time-consuming. For now, we will rely on unit tests to validate the permissions and
        # ensure both cases below are met.
        self.assertTrue(self.browser.title.startswith('Courses') or self.browser.title.startswith('Access Denied'))
