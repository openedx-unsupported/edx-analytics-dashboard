"""
Middleware for Language Preferences
"""

from lang_pref_middleware import middleware


class LanguagePreferenceMiddleware(middleware.LanguagePreferenceMiddleware):
    def get_user_language_preference(self, user):
        """
        Retrieve the given user's language preference.

        Returns None if no preference set.
        """
        return user.language
