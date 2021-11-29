import unittest.mock as mock
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from analytics_dashboard.courses.tests.utils import CourseSamples
from analytics_dashboard.courses.views import CourseValidMixin, AnalyticsV0Mixin, AnalyticsV1Mixin


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


class AnalyticsV0MixinTests(TestCase):
    def setUp(self):
        self.req = RequestFactory()
        self.mixin = AnalyticsV0Mixin()

    def test_default(self):
        r = self.req.get('whatever')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.request, r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL)

    def test_v0(self):
        r = self.req.get('whatever?v=0')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL)

    def test_v1(self):
        r = self.req.get('whatever?v=1')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL_V1)


class AnalyticsV1MixinTests(TestCase):
    def setUp(self):
        self.req = RequestFactory()
        self.mixin = AnalyticsV1Mixin()

    @override_settings(DATA_API_V1_ENABLED=False)
    def test_default_off(self):
        r = self.req.get('whatever')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.request, r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL)

    @override_settings(DATA_API_V1_ENABLED=True)
    def test_default_on(self):
        r = self.req.get('whatever')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL_V1)

    @override_settings(DATA_API_V1_ENABLED=True)
    def test_v0(self):
        r = self.req.get('whatever?v=0')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL)

    @override_settings(DATA_API_V1_ENABLED=True)
    def test_v1(self):
        r = self.req.get('whatever?v=1')
        self.mixin.setup(r)
        self.assertEqual(self.mixin.analytics_client.base_url, settings.DATA_API_URL_V1)
