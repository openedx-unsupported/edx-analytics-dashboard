from hashlib import md5

from soapbox.models import Message
from waffle import switch_is_active

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

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


def translate_dict_values(items, keys):
    """Translates the values of keys in given list of dicts

    Adds the translated values to the dict under a new translated_* key,
    where * is the original key name. The function will skip translating keys
    for which there are already translated_* keys in the dict.

    NOTE: make sure the untranslated string values in the dict are wrapped in a
    ugettext_noop, otherwise the gettext extractor will not find the string and
    it will not be translated.

    Throws a KeyError if any of the dicts does not have a key in given keys.

    Returns True if any key in the keys list was translated, else False.
    """
    did_translate = False
    for item in items:
        for key in keys:
            if 'translated_' + key not in item:
                item['translated_' + key] = _(item[key])
                did_translate = True
    return did_translate


def remove_keys(d, keys):
    """Delete keys from dictionary of nested dictionaries recursively.

    keys can be either:

        a) a tuple of strings representing the keys to remove from the top level of dict d
        b) a dict of strings mapped to tuples specifying the keys to delete in each second level dict of d
        c) a dict of any number of N nested dicts specifying the keys to delete in each Nth level dict of d

    In cases b and c, an empty string ('') key mapped to a tuple specifies the keys to delete in the top level of
    dict d.
    """
    for key, val in d.items():
        if isinstance(val, dict):
            remove_keys(val, keys[key])
        else:
            if isinstance(keys, dict):
                if '' in keys and key in keys['']:
                    del d[key]
            else:
                if key in keys:
                    del d[key]
    return d


def create_fake_soapbox_messages():
    # Importing here so acceptance_tests/__init__.py doesn't start checking for env vars on every management command.
    from acceptance_tests import (SOAPBOX_INACTIVE_MESSAGE, SOAPBOX_GLOBAL_MESSAGE, SOAPBOX_SINGLE_PAGE_MESSAGE,
                                  SOAPBOX_SINGLE_PAGE_VIEW)
    Message.objects.get_or_create(message=SOAPBOX_GLOBAL_MESSAGE, is_active=True, is_global=True)
    Message.objects.get_or_create(message=SOAPBOX_SINGLE_PAGE_MESSAGE, is_active=True, is_global=False,
                                  url=SOAPBOX_SINGLE_PAGE_VIEW)
    Message.objects.get_or_create(message=SOAPBOX_INACTIVE_MESSAGE, is_active=False, is_global=True)


def delete_fake_soapbox_messages():
    from acceptance_tests import (SOAPBOX_INACTIVE_MESSAGE, SOAPBOX_GLOBAL_MESSAGE, SOAPBOX_SINGLE_PAGE_MESSAGE,
                                  SOAPBOX_SINGLE_PAGE_VIEW)
    Message.objects.get(message=SOAPBOX_GLOBAL_MESSAGE, is_active=True, is_global=True).delete()
    Message.objects.get(message=SOAPBOX_SINGLE_PAGE_MESSAGE, is_active=True, is_global=False,
                        url=SOAPBOX_SINGLE_PAGE_VIEW).delete()
    Message.objects.get(message=SOAPBOX_INACTIVE_MESSAGE, is_active=False, is_global=True).delete()
