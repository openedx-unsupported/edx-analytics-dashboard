"""
Middleware for Language Preferences
"""

import logging
from lang_pref_middleware import middleware

from django.template.response import TemplateResponse

from core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class LanguagePreferenceMiddleware(middleware.LanguagePreferenceMiddleware):
    def get_user_language_preference(self, user):
        """
        Retrieve the given user's language preference.

        Returns None if no preference set.
        """
        return user.language


class ServiceUnavailableExceptionMiddleware(object):
    """
    Display an error template for 502 errors.
    """

    def process_exception(self, request, exception):
        if isinstance(exception, ServiceUnavailableError):
            logger.exception(exception)
            return TemplateResponse(request, '503.html', status=503)
