import datetime
import logging

from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver

from social_django.utils import load_strategy

from auth_backends.backends import EdXOpenIdConnect
from django.core.cache import cache

from courses.exceptions import UserNotAssociatedWithBackendError, InvalidAccessTokenError, \
    PermissionsRetrievalFailedError

logger = logging.getLogger(__name__)

# This is the course-level role (defined in the edx-platform course_api
# djangoapp) which we assume while querying the courses list API.  This limits
# the result to courses that only the target user has staff access to.
ROLE_FOR_ALLOWED_COURSES = 'staff'


def _get_course_permission_cache_keys(user):
    """
    Return the cache keys used for user-course permissions
    """
    key_last_updated = 'course_permissions_updated_at_{}'.format(user.id)
    key_courses = 'course_permissions_{}'.format(user.id)
    return key_courses, key_last_updated


def _get_tracking_cache_key(user):
    """
    Return the cache keys used for user tracking_id
    """
    return 'user_tracking_id_{}'.format(user.id)


def set_user_course_permissions(user, courses):
    """
    Sets which courses user is allowed to view.

    Arguments
        user (User)     --  User for which permissions should be set
        courses (list)  --  List of course ID strings
    """
    if not user:
        raise ValueError('User not specified!')

    if courses is None:
        raise ValueError('Courses not specified!')

    # Ensure courses are stored as a list.
    courses = list(courses)

    key_courses, key_last_updated = _get_course_permission_cache_keys(user)

    data = {key_courses: courses, key_last_updated: datetime.datetime.utcnow()}
    cache.set_many(data, settings.COURSE_PERMISSIONS_TIMEOUT)


def revoke_user_course_permissions(user):
    """
    Revokes all course permissions for the given user.

    Arguments
        user (User) --  User for which permissions should be revoked
    """
    cache.delete_many(_get_course_permission_cache_keys(user))


def refresh_user_course_permissions(user):
    """
    Refresh user course permissions from the auth server.

    Arguments
        user (User) --  User whose permissions should be refreshed
    """
    # The authorized courses can come from different claims according to the user role. For example there could be a
    # list of courses the user has access as staff and another that the user has access as instructor. The variable
    # `settings.COURSE_PERMISSIONS_CLAIMS` is a list of the claims that contain the courses.
    claims = settings.COURSE_PERMISSIONS_CLAIMS
    data = _get_user_claims_values(user, claims)
    courses_set = set()
    for claim in claims:
        courses_set.update(data.get(claim, []))
    courses = list(courses_set)

    # If the backend does not provide course permissions, assign no permissions and log a warning as there may be an
    # issue with the backend provider.
    if not courses:
        logger.warning('Authorization server did not return course permissions. Defaulting to no course access.')
        courses = []

    set_user_course_permissions(user, courses)

    return courses


def get_user_tracking_id(user):
    """
    Returns the tracking ID associated with this user or None. The tracking ID
    is cached.
    """
    claim = settings.USER_TRACKING_CLAIM

    if claim is None:
        return None

    cache_key = _get_tracking_cache_key(user)
    tracking_id = cache.get(cache_key)

    if tracking_id is None:
        # if tracking ID not found, then fetch and cache it
        try:
            data = _get_user_claims_values(user, [claim])
            tracking_id = data.get(claim, None)
            cache.set(cache_key, tracking_id)
        except UserNotAssociatedWithBackendError:
            logger.warning('Authorization server did not return tracking claim. Defaulting to None.')
            return None

    return tracking_id


def _get_user_claims_values(user, claims):
    """ Return a list of values associate with the user claims. """
    backend = EdXOpenIdConnect(strategy=load_strategy())
    user_social_auth = user.social_auth.filter(provider=backend.name).first()

    if not user_social_auth:
        raise UserNotAssociatedWithBackendError

    access_token = user_social_auth.extra_data.get('access_token')
    token_type = user_social_auth.extra_data.get('token_type', 'Bearer')

    if not access_token:
        raise InvalidAccessTokenError

    try:
        data = backend.get_user_claims(access_token, claims, token_type=token_type)
    except Exception as e:
        raise PermissionsRetrievalFailedError(e)

    return data


def get_user_course_permissions(user):
    """
    Return list of courses accessible by user.

    Arguments
        user (User) --  User for which course permissions should be returned
    """

    key_courses, key_last_updated = _get_course_permission_cache_keys(user)
    keys = [key_courses, key_last_updated]

    # Check the cache for data
    values = cache.get_many(keys)
    courses = values.get(key_courses, [])

    # If data is not in the cache, refresh the permissions and validate against the new data.
    if not values.get(key_last_updated):
        courses = refresh_user_course_permissions(user)

    return courses


def user_can_view_course(user, course_id):
    """
    Returns boolean indicating if specified user can view specified course.

    Arguments:
        user (User)     --  User whose permissions are being checked
        course_id (str) --  Course to check

    Returns:
        bool -- True, if user can view course; otherwise, False.
    """

    if user.is_superuser:
        return True

    courses = get_user_course_permissions(user)

    return course_id in courses


def _access_token():
    """
    Returns an access token for the Insights service user.

    The access token is retrieved using the Insights OAuth credentials and the
    client credentials grant.  The token is cached for the lifetime of the
    token, as specified by the OAuth provider's response. The token type is
    JWT.

    Returns:
        str: JWT access token
    """
    key = 'oauth2_access_token_{}'
    access_token = cache.get(key)

    if not access_token:
        url = '{root}/access_token'.format(root=settings.BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL)
        access_token, expiration_datetime = EdxRestApiClient.get_oauth_access_token(
            url,
            settings.BACKEND_SERVICE_EDX_OAUTH2_KEY,
            settings.BACKEND_SERVICE_EDX_OAUTH2_SECRET,
            token_type='jwt',
        )
        expires = (expiration_datetime - datetime.datetime.utcnow()).seconds
        cache.set(key, access_token, expires)

    return access_token


# pylint: disable=unused-argument
@receiver(EdXOAuth2.auth_complete_signal)
def on_auth_complete(sender, user, **kwargs):
    """
    Callback to fetch and cache course permissions.
    """
    access_token = _access_token()
    client = EdxRestApiClient(
        settings.COURSE_API_URL,
        jwt=access_token,
    )
    courses = client.courses(
        username=user.username,
        role=ROLE_FOR_ALLOWED_COURSES,
    )
    allowed_courses = set(course['course_id'] for course in courses)
    set_user_course_permissions(user, allowed_courses)
