next_page='/'"""Common settings and globals."""
import ConfigParser

import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path

########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
ENABLE_INSECURE_STATIC_FILES = False
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/New_York'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

LOCALE_PATHS = (
    join(DJANGO_ROOT, 'conf', 'locale'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

FORMAT_MODULE_PATH = 'core.formats'
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(DJANGO_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
COMPRESS_JS_FILTERS = ['compressor.filters.closure.ClosureCompilerFilter']
COMPRESS_CLOSURE_COMPILER_BINARY = 'java -jar scripts/closure-compiler.jar'
COMPRESS_CLOSURE_JS_ARGUMENTS = {'compilation_level': 'ADVANCED_OPTIMIZATIONS',}
COMPRESS_CLOSURE_COMPILER_ARGUMENTS = "--language_in=ECMASCRIPT5"
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = os.environ.get("ANALYTICS_SECRET_KEY", "insecure-secret-key")
########## END SECRET CONFIGURATION


########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
########## END SITE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(DJANGO_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            normpath(join(DJANGO_ROOT, 'templates')),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'core.context_processors.common',
            ],
            'debug': True,
        }
    }
]
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'core.middleware.LanguagePreferenceMiddleware',
    'core.middleware.ServiceUnavailableExceptionMiddleware',
    'courses.middleware.CourseMiddleware',
    'courses.middleware.CoursePermissionsExceptionMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'help.middleware.HelpURLMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    'waffle',
    'django_countries',
    'pinax.announcements',
    'compressor',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'core',
    'courses',
    'django_rjs',
    'help',
    'soapbox',
)

THIRD_PARTY_APPS = (
    'release_util',
    'rest_framework',
    'social_django'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
########## END WSGI CONFIGURATION

########## SEGMENT.IO
# 'None' disables tracking.  This will be turned on for test and production.
SEGMENT_IO_KEY = None

# Regular expression used to identify users that should be ignored in reporting.
# This value will be compiled and should be either a string (e.g. when importing with YAML) or
# a Python regex type.
SEGMENT_IGNORE_EMAIL_REGEX = None
########## END SEGMENT.IO

########## SUPPORT -- Ths value should be overridden for production deployments.
SUPPORT_EMAIL = 'support@example.com'
HELP_URL = None
########## END FEEDBACK

########## LANDING PAGE -- URLs should be overridden for production deployments.
SHOW_LANDING_RESEARCH = True
RESEARCH_URL = 'http://example.com/'
OPEN_SOURCE_URL = 'http://example.com/'
########## END LANDING PAGE

########## DOCUMENTATION LINKS -- These values should be overridden for production deployments.
DOCUMENTATION_LOAD_ERROR_URL = 'http://example.com/'
# evaluated again at the end of production setting after DOCUMENTATION_LOAD_ERROR_URL has been set
DOCUMENTATION_LOAD_ERROR_MESSAGE = '<a href="{error_documentation_link}" target="_blank">Read more</a>.'.format(error_documentation_link=DOCUMENTATION_LOAD_ERROR_URL)
########## END DOCUMENTATION LINKS


########## DATA API CONFIGURATION
DATA_API_URL = 'http://127.0.0.1:9001/api/v0'
DATA_API_AUTH_TOKEN = 'edx'
########## END DATA API CONFIGURATION

# used to determine if a course ID is valid
LMS_COURSE_VALIDATION_BASE_URL = None

# used to construct the shortcut link to course modules
LMS_COURSE_SHORTCUT_BASE_URL = None

# used to construct the shortcut link to view/edit a course in Studio
CMS_COURSE_SHORTCUT_BASE_URL = None

# Used to determine how dates and time are displayed in templates
# The strings are intended for use with the django.utils.dateformat
# module, which uses the PHP's date() style. Format details are
# described at http://www.php.net/date.
DATE_FORMAT = 'F d, Y'
TIME_FORMAT = 'g:i A'

########## AUTHENTICATION
AUTH_USER_MODEL = 'core.User'

# Allow authentication via edX OAuth2/OpenID Connect
AUTHENTICATION_BACKENDS = (
    'auth_backends.backends.EdXOpenIdConnect',
    'django.contrib.auth.backends.ModelBackend',
)

# Set to true if using SSL and running behind a proxy
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'email']

SOCIAL_AUTH_STRATEGY = 'auth_backends.strategies.EdxDjangoStrategy'

# Set these to the correct values for your OAuth2/OpenID Connect provider
SOCIAL_AUTH_EDX_OIDC_KEY = None
SOCIAL_AUTH_EDX_OIDC_SECRET = None
SOCIAL_AUTH_EDX_OIDC_URL_ROOT = None

# This value should be the same as SOCIAL_AUTH_EDX_OIDC_SECRET
SOCIAL_AUTH_EDX_OIDC_ID_TOKEN_DECRYPTION_KEY = None

# Enables a special view that, when accessed, creates and logs in a new user.
# This should NOT be enabled for production deployments!
ENABLE_AUTO_AUTH = False

# Prefix for auto auth usernames. This value MUST be set in order for auto-auth to function. If it were not set
# we would be unable to automatically remove all auto-auth users.
AUTO_AUTH_USERNAME_PREFIX = 'AUTO_AUTH_'

# Maximum time (in seconds) before course permissions expire and need to be refreshed
COURSE_PERMISSIONS_TIMEOUT = 900

LOGIN_REDIRECT_URL = '/courses/'
LOGOUT_REDIRECT_URL = '/'

# Determines if course permissions should be checked before rendering course views.
ENABLE_COURSE_PERMISSIONS = True

# What scopes and claims should be used to get courses
EXTRA_SCOPE = ['permissions', 'course_staff']
COURSE_PERMISSIONS_CLAIMS = ['staff_courses']

# claim for the identifier to track users
USER_TRACKING_CLAIM = 'user_tracking_id'
########## END AUTHENTICATION

# The application and platform display names to be used in templates, emails, etc.
PLATFORM_NAME = 'Your Platform Name Here'
APPLICATION_NAME = 'Insights'
FULL_APPLICATION_NAME = '{0} {1}'.format(PLATFORM_NAME, APPLICATION_NAME)

RJS_OUTPUT_DIR = 'dist'
RJS_OPTIMIZATION_ENABLED = False


########## DOCS/HELP CONFIGURATION
DOCS_ROOT = join(SITE_ROOT, 'docs')

# Load the docs config into memory when the server starts
with open(join(DOCS_ROOT, "config.ini")) as config_file:
    DOCS_CONFIG = ConfigParser.ConfigParser()
    DOCS_CONFIG.readfp(config_file)
########## END DOCS/HELP CONFIGURATION


########## THEME CONFIGURATION
# Path of the SCSS file to use for the site's theme
THEME_SCSS = 'sass/themes/open-edx.scss'
########## END THEME CONFIGURATION

########## COURSE API
COURSE_API_URL = None
GRADING_POLICY_API_URL = None

# If no key is specified, the authenticated user's OAuth2 access token will be used.
COURSE_API_KEY = None
########## END COURSE API

########## MODULE_PREVIEW
MODULE_PREVIEW_URL = None
########## END MODULE_PREVIEW

########## EXTERNAL SERVICE TIMEOUTS
# Time in seconds that Insights should wait on external services
# before giving up.  These values should be overridden in
# configuration.
ANALYTICS_API_DEFAULT_TIMEOUT = 5
LMS_DEFAULT_TIMEOUT = 5
########## END EXTERNAL SERVICE TIMEOUTS

_ = lambda s: s

########## LINKS THAT SHOULD BE SHOWN IN FOOTER
# Example:
# FOOTER_LINKS = (
#     {'url': 'https://www.edx.org', 'text': 'About edX', 'data_role': None},
#     {'url': 'https://www.edx.org/contact-us', 'text': 'Contact Us', 'data_role': None},
#     {'url': 'http://example.com', 'text': 'Terms of Service', 'data_role': 'tos'},
#     {'url': 'http://example.com', 'text': 'Privacy Policy', 'data_role': 'privacy-policy'},
# )
FOOTER_LINKS = (
    {'url': 'http://example.com/', 'text': _('Terms of Service'), 'data_role': 'tos'},
    {'url': 'http://example.com/', 'text': _('Privacy Policy'), 'data_role': 'privacy-policy'},
)
########## END LINKS THAT SHOULD BE SHOWN IN FOOTER

########## REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}
########## END REST FRAMEWORK CONFIGURATION

########## COURSE_ID_PATTERN
# Regex used to capture course_ids from URLs
COURSE_ID_PATTERN = r'(?P<course_id>[^/+]+[/+][^/+]+[/+][^/]+)'
########## END COURSE_ID_PATTERN

########## LEARNER_API_LIST_DOWNLOAD_FIELDS
# Comma-delimited list of field names to include in the Learner List CSV download
# e.g., # "username,segments,cohort,engagements.videos_viewed,last_updated"
# Default (None) includes all available fields, in alphabetical order.
LEARNER_API_LIST_DOWNLOAD_FIELDS = None
########## END LEARNER_API_LIST_DOWNLOAD_FIELDS

########## CACHE CONFIGURATION
COURSE_SUMMARIES_CACHE_TIMEOUT = 3600  # 1 hour timeout
########## END CACHE CONFIGURATION

########## CDN CONFIGURATION
CDN_DOMAIN = None  # production will not use a CDN for static assets if this is set to a falsy value
########## END CDN CONFIGURATION
