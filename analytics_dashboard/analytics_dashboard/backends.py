"""
This file contains Django authentication backends. For more information visit
https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""

from django.conf import settings
from social.backends.oauth import BaseOAuth2


# pylint: disable=abstract-method
class EdXOAuth2(BaseOAuth2):
    name = 'edx-oauth2'
    AUTHORIZATION_URL = '{0}/authorize/'.format(settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT)
    ACCESS_TOKEN_URL = '{0}/access_token/'.format(settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT)
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    ID_KEY = 'username'

    EXTRA_DATA = [
        ('username', 'id'),
        ('access_type', 'access_type', True),
        ('code', 'code'),
        ('expires_in', 'expires'),
        ('refresh_token', 'refresh_token', True),
    ]

    def get_user_details(self, response):
        """Return user details from edX account"""

        return {
            'username': response.get('username'),
            'email': '',
            'fullname': '',
            'first_name': '',
            'last_name': ''
        }
