import json
import logging
from urllib import quote_plus

from ddt import data, ddt
import httpretty
import mock
from requests.exceptions import ConnectionError, Timeout
from testfixtures import LogCapture

from django.conf import settings
from django.test import TestCase

from courses.tests import SwitchMixin
from courses.tests.test_views import DEMO_COURSE_ID, ViewTestMixin


@httpretty.activate
@ddt
class LearnersViewTests(ViewTestMixin, SwitchMixin, TestCase):
    TABLE_ERROR_TEXT = 'We are unable to load this table.'
    viewname = 'courses:learners:learners'

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(LearnersViewTests, cls).setUpClass(*args, **kwargs)
        cls.toggle_switch('enable_learner_analytics', True)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        super(LearnersViewTests, cls).tearDownClass(*args, **kwargs)
        cls.toggle_switch('enable_learner_analytics', False)

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
                course_id=DEMO_COURSE_ID,
            ),
            body=json.dumps(course_metadata_payload),
            status=course_metadata_status
        )
        self.addCleanup(httpretty.reset)

    def _get(self):
        return self.client.get(self.path(course_id=DEMO_COURSE_ID), follow=True)

    def _assert_context(self, response, expected_context_subset):
        default_expected_context_subset = {
            'learner_list_url': '/api/learner_analytics/v0/learners/',
            'course_learner_metadata_url': '/api/learner_analytics/v0/course_learner_metadata/{course_id}/'.format(
                course_id=quote_plus(DEMO_COURSE_ID)
            ),
        }
        self.assertDictContainsSubset(
            dict(default_expected_context_subset.items() + expected_context_subset.items()),
            response.context
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
            'course_learner_metadata_json': course_metadata_payload,
            'show_error': False
        })
        self.assertNotContains(response, self.TABLE_ERROR_TEXT)

    def test_success_if_hidden(self):
        self.toggle_switch('enable_learner_analytics', False)
        self.test_success()

    @data(Timeout, ConnectionError, ValueError)
    def test_data_api_error(self, RequestExceptionClass):
        learners_payload = {'should_not': 'return this value'}
        course_metadata_payload = learners_payload
        self._register_uris(200, learners_payload, 200, course_metadata_payload)
        with mock.patch(
            'learner_analytics_api.v0.clients.LearnerApiResource.get',
            mock.Mock(side_effect=RequestExceptionClass)
        ):
            with LogCapture(level=logging.ERROR) as lc:
                response = self._get()
                self._assert_context(response, {
                    'learner_list_json': {},
                    'course_learner_metadata_json': {},
                    'show_error': True,
                })
                self.assertContains(response, self.TABLE_ERROR_TEXT, 1)
                lc.check(
                    ('courses.views.learners', 'ERROR', 'Failed to reach the Learner List endpoint'),
                    ('courses.views.learners', 'ERROR', 'Failed to reach the Course Learner Metadata endpoint')
                )
