from unittest import TestCase

import requests

from acceptance_tests import DASHBOARD_SERVER_URL


class StatusTests(TestCase):
    POSITIVE_STATUS = u'OK'

    def test_health(self):
        response = requests.get('{}/health'.format(DASHBOARD_SERVER_URL))

        self.assertEqual(response.status_code, 200)

        expected_status = {
            'overall_status': self.POSITIVE_STATUS,
            'detailed_status': {
                'database_connection': self.POSITIVE_STATUS,
                'analytics_api': self.POSITIVE_STATUS
            }
        }
        self.assertDictEqual(response.json(), expected_status)

    def test_status(self):
        response = requests.get('{}/status'.format(DASHBOARD_SERVER_URL))

        self.assertEqual(response.status_code, 200)
