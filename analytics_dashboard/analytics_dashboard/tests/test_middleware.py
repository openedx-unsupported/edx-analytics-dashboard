from django.test import TestCase
from django_dynamic_fixture import G
from lang_pref_middleware.tests import LangPrefMiddlewareTestCaseMixin
from analytics_dashboard.middleware import LanguagePreferenceMiddleware
from analytics_dashboard.models import User


class TestUserLanguagePreferenceMiddleware(LangPrefMiddlewareTestCaseMixin, TestCase):
    middleware_class = LanguagePreferenceMiddleware

    def get_user(self):
        return G(User, language=None)

    def set_user_language_preference(self, user, language):
        user.language = language
        user.save()
