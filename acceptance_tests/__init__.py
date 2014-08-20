import os
from analyticsclient.client import Client

DASHBOARD_SERVER_URL = os.environ.get('DASHBOARD_SERVER_URL', 'http://127.0.0.1:9000')
DASHBOARD_FEEDBACK_EMAIL = os.environ.get('DASHBOARD_FEEDBACK_EMAIL', 'override.this.email@edx.org')


class AnalyticsApiClientMixin(object):
    def setUp(self):
        super(AnalyticsApiClientMixin, self).setUp()

        api_url = os.environ.get('API_SERVER_URL', 'http://127.0.0.1:9001/api/v0')
        auth_token = os.environ.get('API_AUTH_TOKEN', 'edx')
        self.api_client = Client(api_url, auth_token=auth_token, timeout=5)


class FooterMixin(object):
    def test_footer(self):
        self.page.visit()

        # make sure we have the footer
        footer_selector = "div[class=footer]"
        element = self.page.q(css=footer_selector)
        self.assertTrue(element.present)

        # check that we have an email
        selector = footer_selector + " a[class=feedback-email]"
        element = self.page.q(css=selector)
        self.assertEqual(element.text[0], DASHBOARD_FEEDBACK_EMAIL)

        # Verify the terms of service link is present
        selector = footer_selector + " a[role=tos]"
        element = self.page.q(css=selector)
        self.assertEqual(element.text, 'Terms of Service')

        # Verify the privacy policy link is present
        selector = footer_selector + " a[role=privacy-policy]"
        element = self.page.q(css=selector)
        self.assertEqual(element.text, 'Privacy Policy')


def auto_auth(browser, server_url):
    url = '{}/test/auto_auth/'.format(server_url)
    return browser.get(url)
