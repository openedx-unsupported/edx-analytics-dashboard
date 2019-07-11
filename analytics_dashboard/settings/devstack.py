"""django settings for development on devstack"""
from analytics_dashboard.settings.dev import *
from analytics_dashboard.settings.yaml_config import *


DATA_API_URL = os.getenv('DATA_API_URL', DATA_API_URL)
DATA_API_AUTH_TOKEN = os.getenv('DATA_API_AUTH_TOKEN', DATA_API_AUTH_TOKEN)

SOCIAL_AUTH_EDX_OAUTH2_ISSUER = "http://localhost:18000"
SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT = "http://edx.devstack.lms:18000"
SOCIAL_AUTH_EDX_OAUTH2_PUBLIC_URL_ROOT = "http://localhost:18000"
SOCIAL_AUTH_EDX_OAUTH2_LOGOUT_URL = "http://localhost:18000/logout"

BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL = "http://edx.devstack.lms:18000/oauth2"

