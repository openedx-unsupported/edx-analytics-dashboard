import json

import ddt
import httpretty
import mock
from requests.exceptions import ConnectTimeout

from django.conf import settings
from django.test import TestCase

from waffle.testutils import override_flag

from core.tests.test_views import UserTestCaseMixin
from courses.tests.test_views import PermissionsTestMixin


@override_flag('display_learner_analytics', active=True)
@ddt.ddt
class LearnerAPITestMixin(UserTestCaseMixin, PermissionsTestMixin):
    """
    Provides test cases and helper methods for learner analytics api test
    classes.

    Subclasses must override the following properties:

        - endpoint (str): the part of the url following
          '/api/learner_analytics/v0' which identifies the resource, e.g.
          '/learners/'
        - required_query_params (dict): a dict of querystring parameter keys
          and values which are required to make a valid request against the
          endpoint
        - no_permissions_status_code (int): the status code expected to be
          returned when the user is authenticated but does not have permission
          to access the endpoint
    """
    endpoint = ''
    required_query_params = {}
    no_permissions_status_code = None
    content_type = 'application/json'

    @property
    def remote_endpoint(self):
        '''By default, the remote API endpoint matches the local API endpoint.'''
        return self.endpoint

    def assert_response_equals(self, response, expected_status_code, expected_body=None):
        self.assertEqual(response.status_code, expected_status_code)
        if expected_body is not None:
            self.assertEqual(json.loads(response.content), expected_body)

    def test_not_authenticated(self):
        response = self.client.get('/api/learner_analytics/v0' + self.endpoint, self.required_query_params)
        self.assert_response_equals(response, 403, {'detail': 'Authentication credentials were not provided.'})

    def test_no_course_permissions(self):
        self.login()
        response = self.client.get('/api/learner_analytics/v0' + self.endpoint, self.required_query_params)
        self.assert_response_equals(response, self.no_permissions_status_code)

    @mock.patch('learner_analytics_api.v0.clients.LearnerApiResource._request', mock.Mock(side_effect=ConnectTimeout))
    def test_timeout(self):
        self.login()
        self.grant_permission(self.user, 'edX/DemoX/Demo_Course')
        response = self.client.get('/api/learner_analytics/v0' + self.endpoint, self.required_query_params)
        self.assertEqual(response.status_code, 504)

    @ddt.data((200, {'test': 'value'}), (400, {'a': 'b', 'c': 'd'}), (500, {}))
    @ddt.unpack
    @httpretty.activate
    def test_authenticated_and_authorized(self, status_code, body):
        self.login()
        course_id = 'edX/DemoX/Demo_Course'
        self.grant_permission(self.user, course_id)
        httpretty.register_uri(
            httpretty.GET, settings.DATA_API_URL + self.remote_endpoint, body=json.dumps(body), status=status_code,
            content_type=self.content_type,
        )
        response = self.client.get('/api/learner_analytics/v0' + self.endpoint, self.required_query_params)
        self.assert_response_equals(response, status_code, body)


class LearnerDetailViewTestCase(LearnerAPITestMixin, TestCase):
    endpoint = '/learners/username/'
    required_query_params = {'course_id': 'edX/DemoX/Demo_Course'}
    no_permissions_status_code = 404

    def test_no_course_id_provided(self):
        self.login()
        self.grant_permission(self.user, 'edX/DemoX/Demo_Course')
        response = self.client.get('/api/learner_analytics/v0/learners/username/')
        self.assert_response_equals(response, 404, {
            'developer_message': 'Learner username not found.', 'error_code': 'no_learner_for_course'
        })


class LearnerListViewTestCase(LearnerAPITestMixin, TestCase):
    endpoint = '/learners/'
    required_query_params = {'course_id': 'edX/DemoX/Demo_Course'}
    no_permissions_status_code = 403

    def test_no_course_id_provided(self):
        self.login()
        self.grant_permission(self.user, 'edX/DemoX/Demo_Course')
        response = self.client.get('/api/learner_analytics/v0/learners/')
        self.assert_response_equals(response, 403, {'detail': 'You do not have permission to perform this action.'})


@ddt.ddt
class LearnerListCSVTestCase(LearnerListViewTestCase):
    endpoint = '/learners.csv'
    remote_endpoint = '/learners/'
    content_type = 'text/csv'
    course_id = 'edX/DemoX/Demo_Course'

    @httpretty.activate
    def test_headers(self):
        self.login()
        self.grant_permission(self.user, self.course_id)

        # Ensure the extra headers from the remote endpoint get passed through to the response.
        content_disposition = 'attachment; filename=learners.csv'
        httpretty.register_uri(
            httpretty.GET, settings.DATA_API_URL + self.remote_endpoint, body='body',
            status=200, content_type=self.content_type, adding_headers={
                'Content-Disposition': content_disposition,
            },
        )
        response = self.client.get('/api/learner_analytics/v0' + self.endpoint, self.required_query_params)
        self.assertEquals(response['Content-Disposition'], content_disposition)


class EngagementTimelinesViewTestCase(LearnerAPITestMixin, TestCase):
    endpoint = '/engagement_timelines/username/'
    required_query_params = {'course_id': 'edX/DemoX/Demo_Course'}
    no_permissions_status_code = 404

    def test_no_course_id_provided(self):
        self.login()
        self.grant_permission(self.user, 'edX/DemoX/Demo_Course')
        response = self.client.get('/api/learner_analytics/v0/engagement_timelines/username/')
        self.assert_response_equals(response, 404, {
            'developer_message': 'Learner username engagement timeline not found.',
            'error_code': 'no_learner_engagement_timeline'
        })


class CourseLearnerMetadataViewTestCase(LearnerAPITestMixin, TestCase):
    endpoint = '/course_learner_metadata/edX/DemoX/Demo_Course/'
    no_permissions_status_code = 403
