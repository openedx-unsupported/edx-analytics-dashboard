import requests
from slumber import API, exceptions, Resource

from django.conf import settings


class TokenAuth(requests.auth.AuthBase):
    """A requests auth class for DRF-style token-based authentication"""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token {}'.format(self.token)
        return r


class LearnerApiResource(Resource):
    """
    Overrides slumber's default behavior of hiding the requests library's
    response object.  This allows us to return responses directly from the
    Learner Analytics API to the browser.
    """
    def _request(self, *args, **kwargs):
        # Doesn't hide 400s and 500s, however timeouts will still
        # raise a requests.exceptions.ConnectTimeout.
        try:
            response = super(LearnerApiResource, self)._request(*args, **kwargs)
        except exceptions.SlumberHttpBaseException as e:
            response = e.response
        return response

    def _process_response(self, response):
        return response


class LearnerAPIClient(API):
    resource_class = LearnerApiResource

    def __init__(self, timeout=5):
        session = requests.session()
        session.timeout = timeout
        super(LearnerAPIClient, self).__init__(
            settings.DATA_API_URL,
            session=session,
            auth=TokenAuth(settings.DATA_API_AUTH_TOKEN)
        )
