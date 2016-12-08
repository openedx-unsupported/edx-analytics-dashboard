from django.test import TestCase
from django.test.utils import override_settings
import mock

from courses.tests.utils import CourseSamples
from courses.views import CourseValidMixin


class CourseValidMixinTests(TestCase):
    def setUp(self):
        self.mixin = CourseValidMixin()
        self.mixin.course_id = CourseSamples.DEPRECATED_DEMO_COURSE_ID

    @override_settings(LMS_COURSE_VALIDATION_BASE_URL=None)
    def test_no_validation_url(self):
        self.assertTrue(self.mixin.is_valid_course())

    @override_settings(LMS_COURSE_VALIDATION_BASE_URL='a/url')
    @mock.patch('courses.views.requests.get')
    def test_valid_url(self, mock_lms_request):
        mock_lms_request.return_value.status_code = 404
        self.assertFalse(self.mixin.is_valid_course())

        mock_lms_request.return_value.status_code = 200
        self.assertTrue(self.mixin.is_valid_course())
