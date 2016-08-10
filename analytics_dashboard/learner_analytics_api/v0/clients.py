import requests
from slumber import API, exceptions, Resource, serialize

from django.conf import settings


class TokenAuth(requests.auth.AuthBase):
    """A requests auth class for DRF-style token-based authentication"""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token {}'.format(self.token)
        return r


class TextSerializer(serialize.BaseSerializer):
    """
    Slumber API Serializer for text data, e.g. CSV.
    """
    key = 'text'
    content_types = ('text/csv', 'text/plain', )

    def unchanged(self, data):
        """Leaves the request/response data unchanged."""
        return data

    # Define the abstract methods from BaseSerializer
    dumps = loads = unchanged


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
        response.serialized_content = self._try_to_serialize_response(response)
        return response


class LearnerAPIClient(API):
    resource_class = LearnerApiResource

    def __init__(self, timeout=5, serializer_type='json'):
        session = requests.session()
        session.timeout = timeout

        serializers = serialize.Serializer(
            default=serializer_type,
            serializers=[
                serialize.JsonSerializer(),
                serialize.YamlSerializer(),
                TextSerializer(),
            ]
        )
        super(LearnerAPIClient, self).__init__(
            settings.DATA_API_URL,
            session=session,
            auth=TokenAuth(settings.DATA_API_AUTH_TOKEN),
            serializer=serializers,
        )
