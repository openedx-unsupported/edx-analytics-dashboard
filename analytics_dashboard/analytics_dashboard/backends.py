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

    DEFAULT_SCOPE = ['openid', 'profile', 'email'] + settings.COURSE_PERMISSIONS_SCOPE
    ID_TOKEN_ISSUER = settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT
    AUTHORIZATION_URL = '{0}/authorize/'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT)
    ACCESS_TOKEN_URL = '{0}/access_token/'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT)
    USER_INFO_URL = '{0}/user_info/'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT)

    PROFILE_TO_DETAILS_KEY_MAP = {
        'preferred_username': u'username',
        'email': u'email',
        'name': u'full_name',
        'given_name': u'first_name',
        'family_name': u'last_name',
        'locale': u'language',
    }

    def user_data(self, _access_token, *_args, **_kwargs):
        return self.id_token

    def get_user_claims(self, access_token, claims=None):
        """ Returns a dictionary with the values for each claim requested. """
        data = self.get_json(
            self.USER_INFO_URL,
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )

        if claims:
            claims_names = set(claims)
            data = {k: v for (k, v) in data.iteritems() if k in claims_names}

        return data

    def get_user_details(self, response):
        details = self._map_user_details(response)

        locale = response.get('locale')
        if locale:
            details[u'language'] = _to_language(response['locale'])

        return details

    def _map_user_details(self, response):
        """
        Maps key/values from the response to key/values in the user model.

        Does not transfer any key/value that is empty or not present in the reponse.

        """
        dest = {}
        for source_key, dest_key in self.PROFILE_TO_DETAILS_KEY_MAP.items():
            value = response.get(source_key)
            if value:
                dest[dest_key] = value

        return dest


def _to_language(locale):
    """
    Convert locale name to language code if necessary.

    OpenID Connect locale needs to be converted to Django's language
    code. In general however, the differences between the locale names
    and language code are not very clear among different systems.

    See:

      http://openid.net/specs/openid-connect-basic-1_0.html#StandardClaims
      https://docs.djangoproject.com/en/1.6/topics/i18n/#term-translation-string

    """

    return locale.replace('_', '-').lower()
