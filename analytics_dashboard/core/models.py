from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Custom user model. """

    # TODO: it may not be necessary to store the language
    # preferences. Saving it in the session should be enough.
    language = models.CharField(max_length=255, null=True, choices=settings.LANGUAGES, default=None)

    @property
    def access_token(self):
        try:
            return self.social_auth.first().extra_data[u'access_token']  # pylint: disable=no-member
        except Exception:  # pylint: disable=broad-except
            return None

    class Meta(object):
        get_latest_by = 'date_joined'
        db_table = 'analytics_dashboard_user'   # Legacy table name
