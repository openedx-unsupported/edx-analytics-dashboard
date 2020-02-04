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
BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL='http://provider-host/oauth2'
BACKEND_SERVICE_EDX_OAUTH2_KEY='test_backend_oauth2_key'
BACKEND_SERVICE_EDX_OAUTH2_SECRET='test_backend_oauth2_secret'
COURSE_API_URL = 'http://course-api-host/course_ids'
COURSE_API_KEY = 'test_course_api_key'

DATA_API_URL = 'http://data-api-host/api/v0'

LOGGING = get_logger_config(debug=DEBUG, dev_env=True, local_loglevel='DEBUG')
