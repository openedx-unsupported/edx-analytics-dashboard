import json

from requests.exceptions import ConnectTimeout

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.utils import feature_flagged

from .permissions import HasCourseAccessPermission
from .utils import LearnerAPIClient


# TODO: Consider caching responses from the data api when working on AN-6157
@feature_flagged('enable_learner_analytics')
class BaseLearnerApiView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, HasCourseAccessPermission,)

    def __init__(self, *args, **kwargs):
        super(BaseLearnerApiView, self).__init__(*args, **kwargs)
        self.client = LearnerAPIClient()

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

    def get(self, request, api_response, *args, **kwargs):
        """Return the same response as the one from the Data API."""
        return Response(
            json.loads(api_response.content),
            status=api_response.status_code,
            headers=api_response.headers,
        )

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

    def get(self, request, username, **kwargs):
        return super(LearnerDetailView, self).get(request, self.client.learners(username).get(**request.query_params))


class LearnerListView(BaseLearnerApiView):
    """
    Forwards requests to the Learner Analytics API's Learner List endpoint.
    """
    def get(self, request, **kwargs):
        return super(LearnerListView, self).get(request, self.client.learners.get(**request.query_params))


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

    def get(self, request, username, **kwargs):
        return super(EngagementTimelinesView, self).get(
            request, self.client.engagement_timelines(username).get(**request.query_params)
        )


class CourseLearnerMetadataView(BaseLearnerApiView):
    """
    Forwards requests to the Learner Analytics API's Course Metadata endpoint.
    """
    def get(self, request, course_id, **kwargs):
        return super(CourseLearnerMetadataView, self).get(
            request, self.client.course_learner_metadata(course_id).get(**request.query_params)
        )
