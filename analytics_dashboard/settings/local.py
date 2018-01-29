"""Development settings and globals."""

from __future__ import absolute_import

import os
from os.path import join, normpath

from analytics_dashboard.settings.dev import *
from analytics_dashboard.settings.logger import get_logger_config


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(DJANGO_ROOT, 'default.db')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION

########## DATA API CONFIGURATION
DATA_API_URL = os.getenv("API_SERVER_URL", DATA_API_URL)
########## END DATA API CONFIGURATION
