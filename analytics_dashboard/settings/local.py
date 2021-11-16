"""Development settings and globals."""

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
DATA_API_URL_V1 = os.getenv("API_SERVER_URL_V1", DATA_API_URL_V1)
########## END DATA API CONFIGURATION

ENABLE_AUTO_AUTH = True
SOCIAL_AUTH_EDX_OAUTH2_KEY = "insights-sso-key"
SOCIAL_AUTH_EDX_OAUTH2_SECRET = "insights-sso-secret"
SOCIAL_AUTH_EDX_OAUTH2_ISSUER = "http://localhost:18000"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://localhost:18000"
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = "http://localhost:18000/logout"

BACKEND_SERVICE_EDX_OAUTH2_KEY = "insights-backend-service-key"
BACKEND_SERVICE_EDX_OAUTH2_SECRET = "insights-backend-service-secret"
BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = "http://localhost:18000/oauth2"


COURSE_API_URL = 'http://localhost:18000/api/courses/v1/'
GRADING_POLICY_API_URL = 'http://localhost:18000/api/grades/v1/'

# If no key is specified, the authenticated user's OAuth2 access token will be used.
COURSE_API_KEY = None
########## END COURSE API

########## MODULE_PREVIEW
MODULE_PREVIEW_URL = 'http://localhost:18000/xblock'
########## END MODULE_PREVIEW

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}
