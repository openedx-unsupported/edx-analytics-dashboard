from django.test import RequestFactory
from django.utils.unittest.case import TestCase
from courses.middleware import CourseMiddleware


class CourseMiddlewareTests(TestCase):
    def setUp(self):
        super(CourseMiddlewareTests, self).setUp()
        self.factory = RequestFactory()
        self.middleware = CourseMiddleware()

    # pylint: disable=no-member
    def test_course_id(self):
        """
        Verify the middleware sets the course_id attribute on the request.
        """

        # A non-course URL should have course_id set to None
        request = self.factory.get('/')
        self.middleware.process_view(request, '', None, {})
        self.assertIsNone(request.course_id)

        # Course-related URLs should set a course_id on the request
        request = self.factory.get('/')
        course_id = 'edX/DemoX/Demo_Course'
        self.middleware.process_view(request, '', None, {'course_id': course_id})
        self.assertEqual(request.course_id, course_id)
