import json
from django.db import DatabaseError
import mock

from analyticsclient.exceptions import ClientError
from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewTests(TestCase):
    def assertUnhealthyAPI(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        expected = {
            u'overall_status': u'UNAVAILABLE',
            u'detailed_status': {
                u'database_connection': u'OK',
                u'analytics_api': u'UNAVAILABLE'
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    def test_status(self):
        response = self.client.get(reverse('status'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    def test_health(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        expected = {
            u'overall_status': u'OK',
            u'detailed_status': {
                u'database_connection': u'OK',
                u'analytics_api': u'OK'
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=True))
    @mock.patch('django.db.backends.BaseDatabaseWrapper.cursor', mock.Mock(side_effect=DatabaseError))
    def test_health_database_outage(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

        expected = {
            u'overall_status': u'UNAVAILABLE',
            u'detailed_status': {
                u'database_connection': u'UNAVAILABLE',
                u'analytics_api': u'OK'
            }
        }
        self.assertDictEqual(json.loads(response.content), expected)

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(return_value=False))
    def test_health_analytics_api_unhealthy(self):
        self.assertUnhealthyAPI()

    @mock.patch('analyticsclient.status.Status.healthy', mock.PropertyMock(side_effect=ClientError))
    def test_health_analytics_api_unreachable(self):
        self.assertUnhealthyAPI()
