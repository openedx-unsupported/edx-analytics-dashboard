import json

from django.conf import settings

from social.tests.backends.oauth import OAuth2Test
from social.tests.backends.open_id import OpenIdConnectTestMixin


class EdXOAuth2Tests(OAuth2Test):
    backend_path = 'analytics_dashboard.backends.EdXOAuth2'
    expected_username = 'edx'
    access_token_body = json.dumps({
        'access_token': 'foobar',
        'token_type': 'bearer',
        'username': 'edx'
    })

    def test_login(self):
        self.do_login()

    def test_partial_pipeline(self):
        self.do_partial_pipeline()


class EdXOpenIdConnectTests(OpenIdConnectTestMixin, OAuth2Test):
    backend_path = 'analytics_dashboard.backends.EdXOpenIdConnect'
    issuer = settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT
