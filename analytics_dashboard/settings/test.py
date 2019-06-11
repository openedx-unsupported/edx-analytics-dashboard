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

USER_TRACKING_CLAIM = None

LMS_COURSE_SHORTCUT_BASE_URL = 'http://lms-host'
CMS_COURSE_SHORTCUT_BASE_URL = 'http://cms-host'
GRADING_POLICY_API_URL = 'http://grading-policy-api-host'
COURSE_API_URL = 'http://course-api-host'
COURSE_API_KEY = 'test_course_api_key'

DATA_API_URL = 'http://data-api-host/api/v0'
DATA_API_AUTH_TOKEN = 'edx'

LOGGING = get_logger_config(debug=DEBUG, dev_env=True, local_loglevel='DEBUG')

SOCIAL_AUTH_EDX_OIDC_KEY = None
SOCIAL_AUTH_EDX_OIDC_SECRET = None
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = None

MODULE_PREVIEW_URL = None

SECRET_KEY = os.environ.get("ANALYTICS_SECRET_KEY", "insecure-secret-key")

SEGMENT_IO_KEY = None
