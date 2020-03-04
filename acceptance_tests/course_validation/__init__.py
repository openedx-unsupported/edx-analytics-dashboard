from __future__ import absolute_import

import os

from acceptance_tests import str2bool

ENABLE_AUTO_AUTH = str2bool(os.environ.get('ENABLE_AUTO_AUTH', False))
DASHBOARD_SERVER_URL = os.environ['DASHBOARD_SERVER_URL'].strip('/')
API_SERVER_URL = os.environ['API_SERVER_URL']
API_AUTH_TOKEN = os.environ['API_AUTH_TOKEN']

LMS_URL = os.environ.get('LMS_URL')
LMS_USERNAME = os.environ.get('LMS_USERNAME')
LMS_PASSWORD = os.environ.get('LMS_PASSWORD')

BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')
BASIC_AUTH_CREDENTIALS = None

if BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD:
    BASIC_AUTH_CREDENTIALS = (BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD)

COURSE_API_URL = os.environ.get('COURSE_API_URL')
COURSE_API_KEY = os.environ.get('COURSE_API_KEY')
