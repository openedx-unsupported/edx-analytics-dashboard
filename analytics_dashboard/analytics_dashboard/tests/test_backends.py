from django.conf import settings

from social.tests.backends.oauth import OAuth2Test
from social.tests.backends.open_id import OpenIdConnectTestMixin


class EdXOpenIdConnectTests(OpenIdConnectTestMixin, OAuth2Test):
    backend_path = 'analytics_dashboard.backends.EdXOpenIdConnect'
    issuer = settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT
