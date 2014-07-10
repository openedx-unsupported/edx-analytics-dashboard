import json
from django.core.urlresolvers import reverse
from django.test import TestCase


class StatusTests(TestCase):
    def test_status(self):
        response = self.client.get(reverse('status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertDictEqual({'alive': True}, json.loads(response.content))
