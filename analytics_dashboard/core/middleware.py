"""
Middleware for Language Preferences
"""

import logging

from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin
from lang_pref_middleware import middleware

from analytics_dashboard.core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


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
