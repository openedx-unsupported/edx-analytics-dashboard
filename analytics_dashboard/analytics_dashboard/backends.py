"""
This file contains Django authentication backends. For more information visit
https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""

from django.conf import settings

from social.backends.open_id import OpenIdConnectAuth


# pylint: disable=abstract-method
class EdXOpenIdConnect(OpenIdConnectAuth):
    name = 'edx-oidc'

    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    ID_KEY = 'preferred_username'

    DEFAULT_SCOPE = ['openid', 'profile', 'email']
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
            u'last_name': response['family_name'],

            # Optional, scope-specific, data
            u'language': response.get('language')
        }

    def get_user_permissions(self, access_token):
        # TODO: Do we need to worry about refreshing the token?
        data = self.get_json(
            self.USER_INFO_URL,
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )

        return data.get('permissions', {})
