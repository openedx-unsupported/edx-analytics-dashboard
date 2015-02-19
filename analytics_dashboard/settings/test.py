from __future__ import absolute_import
from analytics_dashboard.settings.logger import get_logger_config
from analytics_dashboard.settings.base import *

########## TEST SETTINGS
INSTALLED_APPS += (
    'django_nose',
)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
########## IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

ENABLE_AUTO_AUTH = True
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = 'http://example.com'

LMS_COURSE_SHORTCUT_BASE_URL = 'http://lms-host'
COURSE_API_URL = 'http://course-api-host'

LOGGING = get_logger_config(debug=DEBUG, dev_env=True, local_loglevel='DEBUG')

# Compressing assets slows down view rendering. Since we don't actually need assets, don't bother compressing them.
COMPRESS_ENABLED = False
