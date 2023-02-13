"""django settings for development on devstack"""

from analytics_dashboard.settings.dev import *

DB_OVERRIDES = {
    "PASSWORD": os.environ.get('DB_PASSWORD', DATABASES['default']['PASSWORD']),
    "USER": os.environ.get('DB_USER', DATABASES['default']['USER']),
    "NAME": os.environ.get('DB_NAME', DATABASES['default']['NAME']),
    "HOST": os.environ.get('DB_HOST', DATABASES['default']['HOST']),
    "PORT": os.environ.get('DB_PORT', DATABASES['default']['PORT']),
}

for override, value in DB_OVERRIDES.items():
    DATABASES['default'][override] = value

DATA_API_URL = os.environ.get("API_SERVER_URL", 'http://edx.devstack.analyticsapi:19001/api/v0')
DATA_API_V1_ENABLED = True
DATA_API_URL_V1 = os.environ.get("API_SERVER_URL", 'http://edx.devstack.analyticsapi:19001/api/v1')

ENROLLMENT_AGE_AVAILABLE = True

# Set these to the correct values for your OAuth2/OpenID Connect provider (e.g., devstack)
SOCIAL_AUTH_EDX_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_KEY', 'insights-sso-key')
SOCIAL_AUTH_EDX_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_SECRET', 'insights-sso-secret')
SOCIAL_AUTH_EDX_OAUTH2_ISSUER = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_ISSUER', 'http://localhost:18000')
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT', 'http://edx.devstack.lms:18000')
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = os.environ.get('SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL', 'http://localhost:18000/logout')
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = os.environ.get(
    'SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT', 'http://localhost:18000',
)

BACKEND_SERVICE_EDX_OAUTH2_KEY = os.environ.get('BACKEND_SERVICE_EDX_OAUTH2_KEY', 'insights-backend-service-key')
BACKEND_SERVICE_EDX_OAUTH2_SECRET = os.environ.get(
    'BACKEND_SERVICE_EDX_OAUTH2_SECRET', 'insights-backend-service-secret'
)
BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = os.environ.get(
    'BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL', 'http://edx.devstack.lms:18000/oauth2',
)

COURSE_API_URL = 'http://edx.devstack.lms:18000/api/courses/v1/'
GRADING_POLICY_API_URL = 'http://edx.devstack.lms:18000/api/grades/v1/'

MODULE_PREVIEW_URL = 'http://edx.devstack.lms:18000/xblock'

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}
