from __future__ import absolute_import

import logging

from rest_framework.permissions import BasePermission

from courses.exceptions import PermissionsRetrievalFailedError
from courses.permissions import user_can_view_course

logger = logging.getLogger(__name__)


def user_can_view_learners_in_course(user, course_id):
    """
    Returns whether or not a user can access a particular course within the
    learner API.
    """
    try:
        user_has_permission = user_can_view_course(user, course_id)
    except PermissionsRetrievalFailedError:
        logger.exception(
            "Unable to retrieve course permissions for username=%s in v0",
            user.username,
        )
        user_has_permission = False
    return user_has_permission


class HasCourseAccessPermission(BasePermission):
    """
    Enforces that the requesting user has course access permissions.  Requires
    that view classes have a course_id property for the requested course_id.
    """
    def has_permission(self, request, view):
        return user_can_view_learners_in_course(request.user, view.course_id)
