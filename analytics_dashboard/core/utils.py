from hashlib import md5

from waffle import switch_is_active

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404

from common import clients


User = get_user_model()


def delete_auto_auth_users():
    if not settings.AUTO_AUTH_USERNAME_PREFIX:
        raise ValueError('AUTO_AUTH_USERNAME_PREFIX is not set.')

    User.objects.filter(username__startswith=settings.AUTO_AUTH_USERNAME_PREFIX).delete()


def sanitize_cache_key(key):
    """
    Returns a memcached-safe (no spaces or control characters) key.
    """
    return md5(key.encode("utf-8")).hexdigest()


class CourseStructureApiClient(clients.CourseStructureApiClient):
    """
    A very thin wrapper around `common.clients.CourseStructureApiClient`, which
    defaults the client timeout to `settings.LMS_DEFAULT_TIMEOUT`.
    """
    def __init__(self, url, access_token, timeout=settings.LMS_DEFAULT_TIMEOUT):
        super(CourseStructureApiClient, self).__init__(url, access_token=access_token, timeout=timeout)


def feature_flagged(feature_flag):
    """
    A decorator for class-based views which throws 404s when a waffle
    flag is not enabled.
    """
    def decorator(cls):
        def dispatch(self, request, *args, **kwargs):
            if not switch_is_active(feature_flag):
                raise Http404
            else:
                return super(cls, self).dispatch(request, *args, **kwargs)
        cls.dispatch = dispatch
        return cls
    return decorator
