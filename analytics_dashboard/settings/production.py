"""Production settings and globals."""

from analytics_dashboard.settings.base import *
from analytics_dashboard.settings.yaml_config import *
from analytics_dashboard.settings.logger import get_logger_config

if not DEBUG:
    # Enable offline compression of CSS/JS
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True

    # Use r.js to combine RequireJS files
    RJS_OPTIMIZATION_ENABLED = True

# Minify CSS
COMPRESS_CSS_FILTERS += [
    'compressor.filters.cssmin.CSSMinFilter',
]

LOGGING = get_logger_config()


# ######### HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = ['*']
########## END HOST CONFIGURATION

DB_OVERRIDES = dict(
    PASSWORD=environ.get('DB_MIGRATION_PASS', DATABASES['default']['PASSWORD']),
    ENGINE=environ.get('DB_MIGRATION_ENGINE', DATABASES['default']['ENGINE']),
    USER=environ.get('DB_MIGRATION_USER', DATABASES['default']['USER']),
    NAME=environ.get('DB_MIGRATION_NAME', DATABASES['default']['NAME']),
    HOST=environ.get('DB_MIGRATION_HOST', DATABASES['default']['HOST']),
    PORT=environ.get('DB_MIGRATION_PORT', DATABASES['default']['PORT']),
)

for override, value in DB_OVERRIDES.iteritems():
    DATABASES['default'][override] = value

# Re-declare the full application name in case the components have been overridden.
FULL_APPLICATION_NAME = u'{0} {1}'.format(PLATFORM_NAME, APPLICATION_NAME)

# Depends on DOCUMENTATION_LOAD_ERROR_URL, so evaluate at the end
DOCUMENTATION_LOAD_ERROR_MESSAGE = 'This data may not be available for your course. ' \
                                   '<a href="{error_documentation_link}" target="_blank">Read more</a>.'.format(error_documentation_link=DOCUMENTATION_LOAD_ERROR_URL)
