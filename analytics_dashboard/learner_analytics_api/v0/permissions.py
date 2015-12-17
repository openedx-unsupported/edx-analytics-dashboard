from rest_framework.permissions import BasePermission

from courses.exceptions import UserNotAssociatedWithBackendError
from courses.permissions import user_can_view_course


def user_can_view_learners_in_course(user, course_id):
    """
    Returns whether or not a user can access a particular course within the
    learner API.
    """
    try:
        user_has_permission = user_can_view_course(user, course_id)
    except UserNotAssociatedWithBackendError:
        user_has_permission = False
    return user_has_permission


class HasCourseAccessPermission(BasePermission):
    """
    Enforces that the requesting user has course access permissions.  Requires
    that view classes have a course_id property for the requested course_id.
    """
    def has_permission(self, request, view):
        return user_can_view_learners_in_course(request.user, view.course_id)
