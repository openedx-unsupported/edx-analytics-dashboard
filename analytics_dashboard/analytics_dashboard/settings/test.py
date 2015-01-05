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

LOGGING = get_logger_config(debug=DEBUG, dev_env=True, local_loglevel='DEBUG')
