"""
This file contains Django authentication backends. For more information visit
https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""

from django.conf import settings

from social.backends.oauth import BaseOAuth2
from social.backends.open_id import OpenIdConnectAuth


class EdXOAuth2Mixin(object):
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    USER_INFO_URL = None
    ID_KEY = 'preferred_username'

    def get_user_permissions(self, access_token):
        # TODO: Do we need to worry about refreshing the token?
        data = self.get_json(
            self.USER_INFO_URL,
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )

        return data.get('permissions', {})


# pylint: disable=abstract-method
class EdXOAuth2(EdXOAuth2Mixin, BaseOAuth2):
    name = 'edx-oauth2'
    DEFAULT_SCOPE = ['preferred_username']
    AUTHORIZATION_URL = '{0}/authorize/'.format(settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT)
    ACCESS_TOKEN_URL = '{0}/access_token/'.format(settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT)
    USER_INFO_URL = '{0}/user_info/'.format(settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT)

    EXTRA_DATA = [
        ('preferred_username', 'id'),
        ('code', 'code'),
        ('expires_in', 'expires'),
        ('refresh_token', 'refresh_token', True),
    ]

    def get_user_details(self, response):
        """Return user details from edX account"""

        return {
            'username': response.get('preferred_username'),
            'email': '',
            'fullname': '',
            'first_name': '',
            'last_name': ''
        }


# pylint: disable=abstract-method
class EdXOpenIdConnect(EdXOAuth2Mixin, OpenIdConnectAuth):
    name = 'edx-oidc'
    DEFAULT_SCOPE = ['openid', 'profile']
    ID_TOKEN_ISSUER = settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT
    AUTHORIZATION_URL = '{0}/authorize/'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT)
    ACCESS_TOKEN_URL = '{0}/access_token/'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT)
    USER_INFO_URL = '{0}/user_info/'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT)

    def user_data(self, _access_token, *_args, **_kwargs):
        return self.id_token

    def get_user_details(self, response):
        return {
            u'username': response['preferred_username'],
            u'email': response['email'],
            u'full_name': response['name'],
            u'first_name': response['given_name'],
            u'last_name': response['family_name']
        }
