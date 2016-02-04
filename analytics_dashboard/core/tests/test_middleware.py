import logging

from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase
from django_dynamic_fixture import G
from lang_pref_middleware.tests import LangPrefMiddlewareTestCaseMixin
from testfixtures import LogCapture

from core.exceptions import ServiceUnavailableError
from core.middleware import ServiceUnavailableExceptionMiddleware, LanguagePreferenceMiddleware
from core.models import User


class MiddlewareTestCase(TestCase):
    middleware_class = None

    def setUp(self):
        super(MiddlewareTestCase, self).setUp()
        self.factory = RequestFactory()
        self.middleware = self.middleware_class()   # pylint: disable=not-callable


class MiddlewareAssertionMixin(object):
    def assertStandardExceptions(self, request):
        self.assertIsNone(self.middleware.process_exception(request, None))
        self.assertIsNone(self.middleware.process_exception(request, Exception))
        self.assertIsNone(self.middleware.process_exception(request, ArithmeticError))


class TestUserLanguagePreferenceMiddleware(LangPrefMiddlewareTestCaseMixin, TestCase):
    middleware_class = LanguagePreferenceMiddleware

    def get_user(self):
        return G(User, language=None)

    def set_user_language_preference(self, user, language):
        user.language = language
        user.save()


class ServiceUnavaliableMiddlewareTests(MiddlewareAssertionMixin, MiddlewareTestCase):
    middleware_class = ServiceUnavailableExceptionMiddleware

    def assertIsServiceUnavailableErrorResponse(self, response):
        self.assertEqual(response.status_code, 503)
        self.assertIs(type(response), TemplateResponse)
        self.assertEqual(response.template_name, '503.html')

    def test_process_exception(self):
        request = self.factory.get('/')
        self.assertStandardExceptions(request)
        with LogCapture(level=logging.WARN) as l:
            exception = ServiceUnavailableError()
            response = self.middleware.process_exception(request, exception)
            self.assertIsServiceUnavailableErrorResponse(response)

            # Verify the exception was logged
            l.check(('core.middleware', 'ERROR', str(exception)),)
