from analyticsclient.client import Client
from analyticsclient.exceptions import ClientError
from courses.views import CourseNavBarMixin, CourseView
from django.conf import settings
from django import shortcuts
import logging

logger = logging.getLogger(__name__)


class UsersView(CourseNavBarMixin, CourseView):
    client = None

    def dispatch(self, request, *args, **kwargs):
        self.client = Client(
            base_url=settings.DATA_API_URL,
            auth_token=settings.DATA_API_AUTH_TOKEN,
            timeout=5
        )
        try:
            return super(UsersView, self).dispatch(request, *args, **kwargs)
        except ClientError as e:
            logger.error('API ClientError: %s (%s)', e, e.message)
            return shortcuts.render(request, "users/api-error.html")
