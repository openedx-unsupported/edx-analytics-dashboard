import datetime
import logging

from django.conf import settings
from django.core.cache import cache

from social_django.utils import load_strategy

from auth_backends.backends import EdXOAuth2, EdXOpenIdConnect
from edx_django_utils.monitoring import set_custom_metric
from edx_rest_api_client.client import EdxRestApiClient

from courses.exceptions import (
    AccessTokenRetrievalFailedError,
    InvalidAccessTokenError,
    PermissionsRetrievalFailedError,
    UserNotAssociatedWithBackendError
)

logger = logging.getLogger(__name__)

# This is the course-level role (defined in the edx-platform course_api
# djangoapp) which we assume while querying the courses list API.  This limits
# the result to courses that the target user only has staff access to.
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


def get_user_tracking_id(user):
    """
    Returns the tracking ID associated with this user or None. The tracking ID
    is cached.
    """
    cache_key = _get_tracking_cache_key(user)
    tracking_id = cache.get(cache_key)

    # if tracking ID was not found in cache, fetch and cache it
    if tracking_id is None:
        # first, attempt to get the tracking id from an oauth2 social_auth record
        tracking_id = _get_lms_user_id_from_social_auth(user)

        # if that doesn't yet exist, use the deprecated method using the OIDC backend
        if tracking_id is None:
            tracking_id = _deprecated_get_tracking_id_from_oidc_social_auth(user)
            set_custom_metric('tracking_id_from_social_auth_provider', 'oidc')
        else:
            set_custom_metric('tracking_id_from_social_auth_provider', 'oauth2')

        cache.set(cache_key, tracking_id)

    set_custom_metric('tracking_id', tracking_id)
    return tracking_id


def _get_lms_user_id_from_social_auth(user):
    """ Return the lms user id for the user if found. """
    try:
        return user.social_auth.filter(provider=EdXOAuth2.name).order_by('-id').first().extra_data.get(u'user_id')
    except Exception:  # pylint: disable=broad-except
        logger.warning(u'Exception retrieving lms_user_id from social_auth for user %s.', user.id, exc_info=True)
    return None


def _deprecated_get_tracking_id_from_oidc_social_auth(user):
    """
    Deprecated method for obtaining the tracking id from an OIDC provider.

    Note: This can be removed when OIDC is removed.
    """
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

    claim = settings.USER_TRACKING_CLAIM

    if claim is None:
        return None

    try:
        data = _get_user_claims_values(user, [claim])
        tracking_id = data.get(claim, None)
        return tracking_id
    except UserNotAssociatedWithBackendError:
        logger.warning('Authorization server did not return tracking claim. Defaulting to None for user %s.', user.id)
        return None


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
        courses = _refresh_user_course_permissions(user)

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


def _refresh_user_course_permissions(user):
    """
    Refresh user course permissions from the auth server.

    Arguments
        user (User) --  User whose permissions should be refreshed
    """
    access_token = _fetch_service_user_access_token()
    try:
        client = EdxRestApiClient(
            settings.COURSE_API_URL,
            jwt=access_token,
        )
        courses = client.courses().get(
            username=user.username,
            role=ROLE_FOR_ALLOWED_COURSES,
        )
        allowed_courses = list(set(course['id'] for course in courses))
    except Exception as e:
        raise PermissionsRetrievalFailedError(e)

    set_user_course_permissions(user, allowed_courses)

    return allowed_courses


def _fetch_service_user_access_token():
    """
    Returns an access token for the Insights service user.
    The access token is retrieved using the Insights OAuth credentials and the
    client credentials grant.  The token is cached for the lifetime of the
    token, as specified by the OAuth provider's response. The token type is
    JWT.

    Returns:
        str: JWT access token for the Insights service user.
    """
    key = 'oauth2_access_token'
    access_token = cache.get(key)

    if not access_token:
        try:
            url = '{root}/access_token'.format(root=settings.BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL)
            access_token, expiration_datetime = EdxRestApiClient.get_oauth_access_token(
                url,
                settings.BACKEND_SERVICE_EDX_OAUTH2_KEY,
                settings.BACKEND_SERVICE_EDX_OAUTH2_SECRET,
                token_type='jwt',
            )
            expires = (expiration_datetime - datetime.datetime.utcnow()).total_seconds()
            cache.set(key, access_token, expires)
        except Exception as e:
            raise AccessTokenRetrievalFailedError(e)

    return access_token
