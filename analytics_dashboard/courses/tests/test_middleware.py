import logging

import ddt
from django.http import Http404
from django.template.response import TemplateResponse
from opaque_keys.edx.keys import CourseKey
from testfixtures import LogCapture

from core.tests.test_middleware import MiddlewareTestCase, MiddlewareAssertionMixin
from courses.exceptions import PermissionsRetrievalFailedError
from courses.middleware import CourseMiddleware, CoursePermissionsExceptionMiddleware


class CoursePermissionsExceptionMixin(MiddlewareAssertionMixin):
    def assertIsPermissionsRetrievalFailedResponse(self, response):
        self.assertEqual(response.status_code, 500)
        self.assertIs(type(response), TemplateResponse)
        self.assertEqual(response.template_name, 'courses/permissions-retrieval-failed.html')


@ddt.ddt
class CourseMiddlewareTests(MiddlewareTestCase):
    middleware_class = CourseMiddleware

    # pylint: disable=no-member
    def test_no_course_id(self):
        """
        A non-course URL should have course_id set to None
        """
        request = self.factory.get('/')
        self.middleware.process_view(request, '', None, {})
        self.assertIsNone(request.course_id)
        self.assertIsNone(request.course_key)

    @ddt.data('edX/DemoX/Demo_Course', 'course-v1:edX+DemoX+Demo_2014', 'ccx-v1:edx+1.005x-CCX+rerun+ccx@15')
    def test_course_id(self, course_id):
        """
        Verify the middleware sets the course_id attribute on the request.
        """
        # Course-related URLs should set a course_id and course_key on the request
        request = self.factory.get('/')
        course_key = CourseKey.from_string(course_id)
        self.middleware.process_view(request, '', None, {'course_id': course_id})
        self.assertEqual(request.course_id, course_id)
        self.assertEqual(request.course_key, course_key)

    @ddt.data('edX/DemoX/Demo_Course/Foo', 'course-v1:edX+DemoX')
    def test_invalid_course_id(self, course_id):
        request = self.factory.get('/')
        with self.assertRaises(Http404):
            self.middleware.process_view(request, '', None, {'course_id': course_id})


class CoursePermissionsExceptionMiddlewareTests(CoursePermissionsExceptionMixin, MiddlewareTestCase):
    middleware_class = CoursePermissionsExceptionMiddleware

    def test_process_exception(self):
        request = self.factory.get('/')

        # Method should return None if exception argument is NOT PermissionsRetrievalFailedError.
        self.assertStandardExceptions(request)

        with LogCapture(level=logging.WARN) as l:
            # Method should only return a response for PermissionsRetrievalFailedError.
            exception = PermissionsRetrievalFailedError()
            response = self.middleware.process_exception(request, exception)
            self.assertIsPermissionsRetrievalFailedResponse(response)

            # Verify the exception was logged
            l.check(('courses.middleware', 'ERROR', str(exception)),)
