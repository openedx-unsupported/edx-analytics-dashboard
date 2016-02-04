"""django settings for development on devstack"""
from analytics_dashboard.settings.dev import *
from analytics_dashboard.settings.yaml_config import *


DATA_API_URL = os.getenv('DATA_API_URL', DATA_API_URL)
DATA_API_AUTH_TOKEN = os.getenv('DATA_API_AUTH_TOKEN', DATA_API_AUTH_TOKEN)
