from requests.exceptions import ConnectTimeout

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .clients import LearnerAPIClient
from .permissions import HasCourseAccessPermission
from .renderers import TextRenderer


# TODO: Consider caching responses from the data api when working on AN-6157
class BaseLearnerApiView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, HasCourseAccessPermission,)

    # Serialize the the Learner Analytics API response to JSON, by default.
    serializer_type = 'json'

    # Do not return the HTTP headers from the Data API, by default.
    # This will be further investigated in AN-6928.
    include_headers = False

    def __init__(self, *args, **kwargs):
        super(BaseLearnerApiView, self).__init__(*args, **kwargs)
        self.client = LearnerAPIClient(serializer_type=self.serializer_type)

    def get_queryset(self):
        """
        DRF requires that we override this method.  Since we don't actually use
        querysets/django models in this API, this method doesn't have to return
        anything.
        """
        pass

    @property
    def course_id(self):
        """
        Gets the course_id either from the URL or the querystring parameters.
        """
        course_id = getattr(self.request, 'course_id')
        if not course_id:
            course_id = self.request.query_params.get('course_id')
        return course_id

    def get(self, request, *args, **kwargs):
        """
        Return the response from the Data API.
        """
        api_response = self.get_api_response(request, *args, **kwargs)
        response_kwargs = dict(
            data=api_response.serialized_content,
            status=api_response.status_code,
        )
        if self.include_headers:
            response_kwargs['headers'] = api_response.headers
        return Response(**response_kwargs)

    def get_api_response(self, request, *args, **kwargs):
        """
        Fetch the response from the API.

        Must be implemented by subclasses.
        """
        raise NotImplementedError('Override this method to return the Learner Analytics API response for this view.')

    def handle_exception(self, exc):
        """
        Handles timeouts raised by the API client by returning an HTTP
        504.
        """
        if isinstance(exc, ConnectTimeout):
            return Response(
                data={'developer_message': 'Learner Analytics API timed out.', 'error_code': 'analytics_api_timeout'},
                status=504
            )
        return super(BaseLearnerApiView, self).handle_exception(exc)


class DownloadLearnerApiViewMixin(object):
    """
    Requests text/csv data from the Learner Analytics API, and ensures that the REST framework returns it unparsed,
    including the response headers.
    """
    include_headers = True
    content_type = 'text/csv'
    serializer_type = 'text'

    def get_api_response(self, request, **kwargs):
        """
        Sets the HTTP_ACCEPT header on the request to tell the Learner Analytics API which format to return its data in.

        And tells the REST framework to render as text.  NB: parent class must also define get_api_response()
        """
        request.META['Accept'] = self.content_type
        request.accepted_renderer = TextRenderer()
        return super(DownloadLearnerApiViewMixin, self).get_api_response(request, **kwargs)


class NotFoundLearnerApiViewMixin(object):
    """
    Returns 404s rather than 403s when PermissionDenied exceptions are raised.
    """
    @property
    def not_found_developer_message(self):
        raise NotImplementedError('Override this attribute to define the developer message returned with 404s.')

    @property
    def not_found_error_code(self):
        raise NotImplementedError('Override this attribute to define the error_code string returned with 404s.')

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                data={'developer_message': self.not_found_developer_message, 'error_code': self.not_found_error_code},
                status=404
            )
        return super(NotFoundLearnerApiViewMixin, self).handle_exception(exc)


class LearnerDetailView(NotFoundLearnerApiViewMixin, BaseLearnerApiView):
    """
    Forwards requests to the Learner Analytics API's Learner Detail endpoint.
    """
    not_found_error_code = 'no_learner_for_course'

    @property
    def not_found_developer_message(self):
        message = 'Learner {} not found'.format(self.kwargs.get('username', ''))
        message += 'for course {}.'.format(self.course_id) if self.course_id else '.'
        return message

    def get_api_response(self, request, username, **kwargs):
        return self.client.learners(username).get(**request.query_params)


class LearnerListView(BaseLearnerApiView):
    """
    Forwards requests to the Learner Analytics API's Learner List endpoint.
    """
    def get_api_response(self, request, **kwargs):
        return self.client.learners.get(**request.query_params)


class LearnerListCSV(DownloadLearnerApiViewMixin, LearnerListView):
    """
    Forwards text/csv requests to the Learner Analytics API's Learner List endpoint,
    and returns a simple text response.
    """
    pass


class EngagementTimelinesView(NotFoundLearnerApiViewMixin, BaseLearnerApiView):
    """
    Forwards requests to the Learner Analytics API's Engagement Timeline
    endpoint.
    """
    not_found_error_code = 'no_learner_engagement_timeline'

    @property
    def not_found_developer_message(self):
        message = 'Learner {} engagement timeline not found'.format(self.kwargs.get('username', ''))
        message += 'for course {}.'.format(self.course_id) if self.course_id else '.'
        return message

    def get_api_response(self, request, username, **kwargs):
        return self.client.engagement_timelines(username).get(**request.query_params)


class CourseLearnerMetadataView(BaseLearnerApiView):
    """
    Forwards requests to the Learner Analytics API's Course Metadata endpoint.
    """
    def get_api_response(self, request, course_id, **kwargs):
        return self.client.course_learner_metadata(course_id).get(**request.query_params)
