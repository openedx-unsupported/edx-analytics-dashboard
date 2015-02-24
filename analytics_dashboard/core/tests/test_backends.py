from django.conf import settings

from social.tests.backends.oauth import OAuth2Test
from social.tests.backends.open_id import OpenIdConnectTestMixin

from courses.permissions import get_user_course_permissions


DUMMY_AUTHORIZED_COURSE = 'dummy/course/id'


class EdXOpenIdConnectTests(OpenIdConnectTestMixin, OAuth2Test):
    backend_path = 'auth_backends.backends.EdXOpenIdConnect'
    issuer = settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT
    expected_username = 'test_user'

    def get_id_token(self, *args, **kwargs):
        data = super(EdXOpenIdConnectTests, self).get_id_token(*args, **kwargs)

        # Set the field used to derive the username of the logged user.
        data['preferred_username'] = self.expected_username

        # Include a dummy list of authorized courses.
        claim_name = settings.COURSE_PERMISSIONS_CLAIMS[0]
        data[claim_name] = [DUMMY_AUTHORIZED_COURSE]

        return data

    def test_course_permissions(self):
        user = self.do_login()
        authorized_courses = get_user_course_permissions(user)

        self.assertEqual(len(authorized_courses), 1)
        self.assertIn(DUMMY_AUTHORIZED_COURSE, authorized_courses)
