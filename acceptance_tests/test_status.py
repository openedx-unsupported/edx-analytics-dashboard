from unittest import TestCase

import requests

from acceptance_tests import DASHBOARD_SERVER_URL


class StatusTests(TestCase):
    POSITIVE_STATUS = 'OK'

    def test_health(self):
        response = requests.get(f'{DASHBOARD_SERVER_URL}/health')

        self.assertEqual(response.status_code, 200)

        expected_status = {
            'overall_status': self.POSITIVE_STATUS,
            'detailed_status': {
                'database_connection': self.POSITIVE_STATUS,
            }
        }
        self.assertDictEqual(response.json(), expected_status)

    def test_status(self):
        response = requests.get(f'{DASHBOARD_SERVER_URL}/status')

        self.assertEqual(response.status_code, 200)
