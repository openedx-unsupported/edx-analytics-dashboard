from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.

    """

    # TODO: it may not be necessary to store the language
    # preferences. Saving it in the session should be enough.
    language = models.CharField(max_length=255, null=True, choices=settings.LANGUAGES, default=None)

    class Meta(object):
        get_latest_by = 'date_joined'
