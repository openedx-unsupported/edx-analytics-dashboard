from django.test import TestCase
from django_dynamic_fixture import G
from social_django.models import UserSocialAuth

from core.models import User


class UserTests(TestCase):
    def test_access_token(self):
        user = G(User)
        self.assertIsNone(user.access_token)

        social_auth = G(UserSocialAuth, user=user)
        self.assertIsNone(user.access_token)

        access_token = u'My voice is my passport. Verify me.'
        social_auth.extra_data[u'access_token'] = access_token
        social_auth.save()
        self.assertEqual(user.access_token, access_token)

    def test_multiple_access_tokens(self):
        """ Ensures the correct access token is pulled from the insights user when multiple social auth entries
        exist for that user. """
        user = G(User)
        self.assertIsNone(user.access_token)

        lms_user_id = 6181
        expected_access_token = 'access_token_3'
        UserSocialAuth.objects.create(user=user, provider='edx-oidc', uid='older_6181',
                                      extra_data={'user_id': lms_user_id, 'access_token': 'access_token_1'})
        UserSocialAuth.objects.create(user=user, provider='edx-oauth2', uid='older_6181',
                                      extra_data={'user_id': lms_user_id, 'access_token': 'access_token_2'})
        UserSocialAuth.objects.create(user=user, provider='edx-oauth2',
                                      extra_data={'user_id': lms_user_id, 'access_token': expected_access_token})

        same_user = User.objects.get(id=user.id)
        self.assertEqual(same_user.social_auth.count(), 3)
        self.assertEqual(same_user.access_token, expected_access_token)
