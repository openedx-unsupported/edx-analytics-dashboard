import logging

from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase
from opaque_keys.edx.keys import CourseKey
from testfixtures import LogCapture

from courses.exceptions import PermissionsRetrievalFailedError
from courses.middleware import CourseMiddleware, CoursePermissionsExceptionMiddleware


class MiddlewareTestCase(TestCase):
    middleware_class = None

    def setUp(self):
        super(MiddlewareTestCase, self).setUp()
        self.factory = RequestFactory()
        self.middleware = self.middleware_class()   # pylint: disable=not-callable


class MiddlewareAssertionMixin(object):
    def assertIsPermissionsRetrievalFailedResponse(self, response):
        self.assertEqual(response.status_code, 500)
        self.assertIs(type(response), TemplateResponse)
        self.assertEqual(response.template_name, 'courses/permissions-retrieval-failed.html')


class CourseMiddlewareTests(MiddlewareTestCase):
    middleware_class = CourseMiddleware

    # pylint: disable=no-member
    def test_course_id(self):
        """
        Verify the middleware sets the course_id attribute on the request.
        """

        # A non-course URL should have course_id set to None
        request = self.factory.get('/')
        self.middleware.process_view(request, '', None, {})
        self.assertIsNone(request.course_id)
        self.assertIsNone(request.course_key)

        # Course-related URLs should set a course_id and course_key on the request
        request = self.factory.get('/')
        course_id = 'edX/DemoX/Demo_Course'
        course_key = CourseKey.from_string(course_id)
        self.middleware.process_view(request, '', None, {'course_id': course_id})
        self.assertEqual(request.course_id, course_id)
        self.assertEqual(request.course_key, course_key)


class CoursePermissionsExceptionMiddlewareTests(MiddlewareAssertionMixin, MiddlewareTestCase):
    middleware_class = CoursePermissionsExceptionMiddleware

    def test_process_exception(self):
        request = self.factory.get('/')

        # Method should return None if exception argument is NOT PermissionsRetrievalFailedError.
        self.assertIsNone(self.middleware.process_exception(request, None))
        self.assertIsNone(self.middleware.process_exception(request, Exception))
        self.assertIsNone(self.middleware.process_exception(request, ArithmeticError))

        with LogCapture(level=logging.WARN) as l:
            # Method should only return a response for PermissionsRetrievalFailedError.
            exception = PermissionsRetrievalFailedError()
            response = self.middleware.process_exception(request, exception)
            self.assertIsPermissionsRetrievalFailedResponse(response)

            # Verify the exception was logged
            l.check(('courses.middleware', 'ERROR', str(exception)),)
