from django.contrib import messages

from django.contrib.messages.api import MessageFailure
from django.shortcuts import redirect
from django.utils.http import urlquote

from social.exceptions import SocialAuthBaseException

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware


class PatchedSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    """
    This patched middleware gets the backend from the request instead of the strategy.
    It is unclear when/where strategy.backend should be set. If https://github.com/omab/python-social-auth/issues/350
    is fixed, this middleware should be removed in favor of the parent class.
    """

    def process_exception(self, request, exception):
        strategy = getattr(request, 'social_strategy', None)
        if strategy is None or self.raise_exception(request, exception):
            return

        if isinstance(exception, SocialAuthBaseException):
            # The line below is the patch. Use request.backend instead of strategy.backend.
            backend_name = request.backend.name
            message = self.get_message(request, exception)
            url = self.get_redirect_uri(request, exception)
            try:
                messages.error(request, message,
                               extra_tags='social-auth ' + backend_name)
            except MessageFailure:
                url += ('?' in url and '&' or '?') + 'message={0}&backend={1}'.format(urlquote(message), backend_name)

            return redirect(url)
