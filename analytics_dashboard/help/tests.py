from django import http
from django.template.response import TemplateResponse
from django.test import TestCase
from help import HELP_CONTEXT_TOKEN_NAME

from help.middleware import HelpURLMiddleware
from help.utils import get_doc_url


DOC_BASE_URL = 'http://edx-insights.readthedocs.org/en/latest'


def build_doc_url(path):
    return '{0}/{1}'.format(DOC_BASE_URL, path)


DOC_INDEX = build_doc_url('index.html')
DOC_ENROLLMENT_ACTIVITY = build_doc_url('enrollment/Enrollment_Activity.html')


class HelpURLMiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = HelpURLMiddleware()

    def assertHelpURLEqual(self, page_token, expected_url):
        request = http.HttpRequest()

        context = {}
        if page_token is not None:
            context[HELP_CONTEXT_TOKEN_NAME] = page_token

        response = TemplateResponse(request, None, context)

        response = self.middleware.process_template_response(request, response)
        self.assertEqual(response.context_data['help_url'], expected_url)

    def test_process_template_response(self):
        # If the context has no page_token set, help_url should be set to the default docs page.
        self.assertHelpURLEqual(None, DOC_INDEX)

        # If the context has an invalid page_token set, help_url should be set to the default docs page.
        self.assertHelpURLEqual('Not a real token', DOC_INDEX)

        # If the context has a valid page_token set, help_url should be set to the corresponding docs page.
        self.assertHelpURLEqual('course_enrollment_activity', DOC_ENROLLMENT_ACTIVITY)

    def test_process_template_response_with_error(self):
        """
        The middleware should NOT process error responses.
        """
        response = http.HttpResponseServerError()
        request = http.HttpRequest()
        response = self.middleware.process_template_response(request, response)
        self.assertFalse(hasattr(response, 'context_data'))


class UtilsTests(TestCase):
    def assertValidDocURL(self, page_token, expected_url):
        actual = get_doc_url(page_token)
        self.assertEqual(actual, expected_url)

    def test_get_doc_url(self):
        # If no page_token passed, return the default docs page.
        self.assertValidDocURL(None, DOC_INDEX)

        # If an invalid page_token passed, return the default docs page.
        self.assertValidDocURL('Not a real token', DOC_INDEX)

        # If valid page_token passed, return the corresponding docs page.
        self.assertValidDocURL('course_enrollment_activity', DOC_ENROLLMENT_ACTIVITY)
