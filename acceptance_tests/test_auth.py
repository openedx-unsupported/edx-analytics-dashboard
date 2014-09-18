from bok_choy.web_app_test import WebAppTest

from acceptance_tests import USERNAME, PASSWORD, ENABLE_OAUTH_AUTHORIZE
from pages import LoginPage


class OAuthFlowTests(WebAppTest):
    def setUp(self):
        """
        Instantiate the page objects.
        """
        super(OAuthFlowTests, self).setUp()

        self.login_page = LoginPage(self.browser)

        self.username = USERNAME
        self.password = PASSWORD

    def test_login(self):
        # Visit login URL and get redirected
        self.login_page.visit()

        # Input credentials and authorize
        self.login_page.q(css='input[name=username]').fill(self.username)
        self.login_page.q(css='input[name=password]').fill(self.password)
        self.login_page.q(css='button[type=submit]').click()

        if ENABLE_OAUTH_AUTHORIZE:
            self.login_page.q(css='input[name=authorize]').click()

        # User should arrive at course index page (or access denied page, if no permissions)
        # Splitting this out into two separate tests would require two separate sets of credentials. That is
        # feasible, but somewhat time-consuming. For now, we will rely on unit tests to validate the permissions and
        # ensure both cases below are met.
        self.assertTrue(self.browser.title.startswith('Courses') or self.browser.title.startswith('Access Denied'))
