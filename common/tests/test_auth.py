from unittest import TestCase

import httpretty
import requests

from common.auth import BearerAuth


class BearerAuthTests(TestCase):
    @httpretty.activate
    def test_headers(self):
        """
        Verify the class adds an Authorization header that includes the token.
        :return:
        """

        token = 'this-is-a-test'
        url = 'http://example.com/'

        # Mock the HTTP response and issue the request
        httpretty.register_uri(httpretty.GET, url)
        requests.get(url, auth=BearerAuth(token))

        # Verify the header was set on the request
        self.assertEqual(httpretty.last_request().headers['Authorization'], 'Bearer {0}'.format(token))
