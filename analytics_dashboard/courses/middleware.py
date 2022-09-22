"""
This file contains Django middleware. For more information visit
https://docs.djangoproject.com/en/dev/topics/http/middleware/.
"""


import logging

from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from analytics_dashboard.courses.exceptions import PermissionsRetrievalFailedError

logger = logging.getLogger(__name__)


class CourseMiddleware(MiddlewareMixin):
    """
    Adds course info to the request object.
    """

    def process_view(self, request, _view_func, _view_args, view_kwargs):
        request.course_key = None
        request.course_id = None

        course_id = view_kwargs.get('course_id', None)

        if course_id:
            try:
                request.course_key = CourseKey.from_string(course_id)
            except InvalidKeyError as e:
                # Raising an InvalidKeyError here causes a 500-level error which alerts devops. This should really be a
                # 404 error because though the course requested cannot be found, the server is operating correctly.
                raise Http404 from e
            request.course_id = str(request.course_key)


class CoursePermissionsExceptionMiddleware(MiddlewareMixin):
    """
    Display an error template for PermissionsNotFoundError exceptions.
    """

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionsRetrievalFailedError):
            logger.exception(exception)
            return TemplateResponse(request, 'courses/permissions-retrieval-failed.html', status=500)

        return None
