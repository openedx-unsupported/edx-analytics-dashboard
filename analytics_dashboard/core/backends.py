"""
This file contains Django authentication backends. For more information visit
https://docs.djangoproject.com/en/dev/topics/auth/customizing/.
"""
import json

from django.conf import settings
import django.dispatch
from social.backends.open_id import OpenIdConnectAuth
from waffle import switch_is_active


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

    auth_complete_signal = django.dispatch.Signal(providing_args=["user", "id_token"])

    def user_data(self, _access_token, *_args, **_kwargs):
        # Include decoded id_token fields in user data.
        return self.id_token

    def auth_complete_params(self, state=None):
        params = super(EdXOpenIdConnect, self).auth_complete_params(state)

        # TODO: Due a limitation in the oidc provider in the LMS, the list of all course permissions
        # is computed during the authentication process. As an optimization, we explicitly request
        # the list here, avoiding further roundtrips. This is no longer necessary once the limitation
        # is resolved and instead the course permissions can be requested on a need to have basis,
        # reducing overhead significantly.
        claim_names = settings.COURSE_PERMISSIONS_CLAIMS
        courses_claims_request = {name: {'essential': True} for name in claim_names}
        params['claims'] = json.dumps({'id_token': courses_claims_request})

        return params

    def auth_complete(self, *args, **kwargs):
        # WARNING: during testing, the user model class is `social.tests.models` and not the one
        # specified for the application.
        user = super(EdXOpenIdConnect, self).auth_complete(*args, **kwargs)
        self.auth_complete_signal.send(sender=self.__class__, user=user, id_token=self.id_token)
        return user

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

        # Set superuser bit if the provider determines the user is an administrator
        details[u'is_superuser'] = details[u'is_staff'] = response.get('administrator', False)

        return details

    def _map_user_details(self, response):
        """
        Maps key/values from the response to key/values in the user model.

        Does not transfer any key/value that is empty or not present in the reponse.

        """
        dest = {}
        for source_key, dest_key in self.PROFILE_TO_DETAILS_KEY_MAP.items():
            value = response.get(source_key)
            if value is not None:
                dest[dest_key] = value

        return dest

    def get_scope(self):
        scope = super(EdXOpenIdConnect, self).get_scope()

        if switch_is_active('enable_oidc_permissions_scope'):
            scope.append('permissions')

        return scope


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
