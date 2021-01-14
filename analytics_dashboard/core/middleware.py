"""
Middleware for Language Preferences
"""

import logging

from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin
from lang_pref_middleware import middleware

from analytics_dashboard.core.exceptions import ServiceUnavailableError
from analytics_dashboard.settings.waffle import IGNORE_ACCEPT_LANGUAGE

logger = logging.getLogger(__name__)


def language_header_preempt_middleware(get_response):
    """
    If the appropriate waffle flag is present, ignore the 'Accept-Language' header.
    """
    def middleware(request):
        """
        Prepared middleware closure for Accept-Language header check.
        """
        if IGNORE_ACCEPT_LANGUAGE.is_enabled() and 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']
        return get_response(request)

    return middleware


class LanguagePreferenceMiddleware(middleware.LanguagePreferenceMiddleware, MiddlewareMixin):
    def get_user_language_preference(self, user):
        """
        Retrieve the given user's language preference.

        Returns None if no preference set.
        """
        return user.language


class ServiceUnavailableExceptionMiddleware(MiddlewareMixin):
    """
    Display an error template for 502 errors.
    """

    def process_exception(self, request, exception):
        if isinstance(exception, ServiceUnavailableError):
            logger.exception(exception)
            return TemplateResponse(request, '503.html', status=503)

        return None
