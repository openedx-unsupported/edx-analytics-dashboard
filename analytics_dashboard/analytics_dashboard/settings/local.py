"""Development settings and globals."""

from __future__ import absolute_import

import os
from os.path import join, normpath

from analytics_dashboard.settings.base import *
from analytics_dashboard.settings.logger import get_logger_config


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


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


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION


########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup

if os.environ.get('ENABLE_DJANGO_TOOLBAR', False):
    INSTALLED_APPS += (
        'debug_toolbar',
    )

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION

INSTALLED_APPS += (
    'django_nose',
)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

LMS_COURSE_SHORTCUT_BASE_URL = 'https://courses.edx.org/courses'

########## BRANDING
PLATFORM_NAME = 'edX'
APPLICATION_NAME = 'Insights'
FULL_APPLICATION_NAME = '{0} {1}'.format(PLATFORM_NAME, APPLICATION_NAME)
########## END BRANDING


########## AUTHENTICATION/AUTHORIZATION
# Set these to the correct values for your OAuth2/OpenID Connect provider
SOCIAL_AUTH_EDX_OIDC_KEY = 'dummy-key'
SOCIAL_AUTH_EDX_OIDC_SECRET = 'dummy-secret'
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = 'http://0.0.0.0:8000/oauth2'

# This value should be the same as SOCIAL_AUTH_EDX_OIDC_SECRET
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = 'dummy-decryption-key'

ENABLE_AUTO_AUTH = True

# Uncomment the line below to avoid having to worry about course permissions
ENABLE_COURSE_PERMISSIONS = False
########## END AUTHENTICATION/AUTHORIZATION

########## FEEDBACK AND SUPPORT
HELP_URL = '#'
########## END FEEDBACK

########## SEGMENT.IO
# 'None' disables tracking.  This will be turned on for test and production.
SEGMENT_IO_KEY = os.environ.get('SEGMENT_WRITE_KEY')
########## END SEGMENT.IO

LOGGING = get_logger_config(debug=DEBUG, dev_env=True, local_loglevel='DEBUG')

COURSE_API_URL = 'http://127.0.0.1:8000/api'
COURSE_API_KEY = 'edx'
