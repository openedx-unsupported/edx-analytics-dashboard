import os

DASHBOARD_SERVER_URL = os.environ.get('DASHBOARD_SERVER_URL', 'http://127.0.0.1:9000')
API_SERVER_URL = os.environ.get('API_SERVER_URL', 'http://127.0.0.1:9001/api/v0')
API_AUTH_TOKEN = os.environ.get('API_AUTH_TOKEN', 'edx')
