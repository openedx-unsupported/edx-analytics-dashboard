

import json
import logging

import unittest.mock as mock
import httpretty
from ddt import data, ddt
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout
from testfixtures import LogCapture
from waffle.testutils import override_flag, override_switch

from analytics_dashboard.courses.tests.test_views import ViewTestMixin
from analytics_dashboard.courses.tests.utils import assert_dict_contains_subset, CourseSamples


@httpretty.activate
@override_flag('display_learner_analytics', active=True)
@ddt
class LearnersViewTests(ViewTestMixin, TestCase):
    TABLE_ERROR_TEXT = 'We are unable to load this table.'
    viewname = 'courses:learners:learners'

    def _register_uris(self, learners_status, learners_payload, course_metadata_status, course_metadata_payload):
        httpretty.register_uri(
            httpretty.GET,
            '{data_api_url}/learners/'.format(data_api_url=settings.DATA_API_URL),
            body=json.dumps(learners_payload),
            status=learners_status
        )
        httpretty.register_uri(
            httpretty.GET,
            '{data_api_url}/course_learner_metadata/{course_id}/'.format(
                data_api_url=settings.DATA_API_URL,
                course_id=CourseSamples.DEMO_COURSE_ID,
            ),
            body=json.dumps(course_metadata_payload),
            status=course_metadata_status
        )
        self.addCleanup(httpretty.reset)

    def _get(self):
        return self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID))

    def _assert_context(self, response, expected_context_subset):
        default_expected_context_subset = {
            'learner_list_url': '/api/learner_analytics/v0/learners/',
            'course_learner_metadata_url': '/api/learner_analytics/v0/course_learner_metadata/{course_id}/'.format(
                course_id=CourseSamples.DEMO_COURSE_ID
            ),
        }
        assert_dict_contains_subset(response.context, dict(list(expected_context_subset.items())))
        assert_dict_contains_subset(
            response.context['js_data']['course'],
            dict(list(default_expected_context_subset.items())),
        )

    def get_mock_data(self, *args, **kwargs):
        pass

    def test_success(self):
        learners_payload = {'arbitrary_learners_key': ['arbitrary_value_1', 'arbitrary_value_2']}
        course_metadata_payload = {'arbitrary_metadata_value': {'arbitrary_value_1': 'arbitrary_value_2'}}
        self._register_uris(200, learners_payload, 200, course_metadata_payload)
        response = self._get()
        self._assert_context(response, {
            'learner_list_json': learners_payload,
            'course_learner_metadata_json': course_metadata_payload
        })
        self.assertNotContains(response, self.TABLE_ERROR_TEXT)
        return response

    @override_flag('display_learner_analytics', active=False)
    def test_success_if_hidden(self):
        self.test_success()

    @override_switch('enable_learner_download', active=False)
    def test_disable_learner_download_button(self):
        response = self.test_success()
        self.assertNotIn('learner_list_download_url', response.context['js_data']['course'])

    @override_switch('enable_learner_download', active=True)
    @override_settings(LEARNER_API_LIST_DOWNLOAD_FIELDS=None)
    def test_enable_learner_download_button(self):
        response = self.test_success()
        self.assertEqual(response.context['js_data']['course']['learner_list_download_url'],
                         '/api/learner_analytics/v0/learners.csv')

    @override_switch('enable_learner_download', active=True)
    @override_settings(LEARNER_API_LIST_DOWNLOAD_FIELDS='username,email')
    def test_enable_learner_download_button_with_fields(self):
        response = self.test_success()
        self.assertEqual(response.context['js_data']['course']['learner_list_download_url'],
                         '/api/learner_analytics/v0/learners.csv?fields=username%2Cemail')

    @data(Timeout, RequestsConnectionError, ValueError)
    def test_data_api_error(self, RequestExceptionClass):
        learners_payload = {'should_not': 'return this value'}
        course_metadata_payload = learners_payload
        self._register_uris(200, learners_payload, 200, course_metadata_payload)

        # False positive https://github.com/PyCQA/pylint/issues/289
        # pylint: disable=bad-continuation
        with mock.patch(
            'analytics_dashboard.learner_analytics_api.v0.clients.LearnerApiResource.get',
            mock.Mock(side_effect=RequestExceptionClass),
        ):
            with LogCapture(level=logging.ERROR) as lc:
                response = self._get()
                self._assert_context(response, {
                    'learner_list_json': 'Failed to reach the Learner List endpoint',
                    'course_learner_metadata_json': 'Failed to reach the Course Learner Metadata endpoint'
                })
                lc.check(
                    (
                        'analytics_dashboard.courses.views.learners',
                        'ERROR',
                        'Failed to reach the Learner List endpoint',
                    ),
                    (
                        'analytics_dashboard.courses.views.learners',
                        'ERROR',
                        'Failed to reach the Course Learner Metadata endpoint',
                    ),
                )
