import locale
import os

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def str2bool(s):
    s = unicode(s)
    return s.lower() in (u"yes", u"true", u"t", u"1")

# Dashboard settings
DASHBOARD_SERVER_URL = os.environ.get('DASHBOARD_SERVER_URL', 'http://127.0.0.1:9000')
DASHBOARD_FEEDBACK_EMAIL = os.environ.get('DASHBOARD_FEEDBACK_EMAIL', 'override.this.email@example.com')
PLATFORM_NAME = os.environ.get('PLATFORM_NAME', 'edX')
APPLICATION_NAME = os.environ.get('APPLICATION_NAME', 'Insights')
SUPPORT_URL = os.environ.get('SUPPORT_URL', 'http://example.com/')

# Analytics data API settings
API_SERVER_URL = os.environ['API_SERVER_URL']
API_AUTH_TOKEN = os.environ['API_AUTH_TOKEN']

# Test configuration
ENABLE_AUTO_AUTH = str2bool(os.environ.get('ENABLE_AUTO_AUTH', False))
ENABLE_OAUTH_TESTS = str2bool(os.environ.get('ENABLE_AUTH_TESTS', True))
ENABLE_ERROR_PAGE_TESTS = str2bool(os.environ.get('ENABLE_ERROR_PAGE_TESTS', True))

# LMS settings
BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')
LMS_HOSTNAME = os.environ.get('LMS_HOSTNAME')
LMS_USERNAME = os.environ.get('LMS_USERNAME')
LMS_PASSWORD = os.environ.get('LMS_PASSWORD')

if ENABLE_OAUTH_TESTS and not (LMS_HOSTNAME and LMS_USERNAME and LMS_PASSWORD):
    raise Exception('LMS settings must be set in order to test OAuth.')

TEST_COURSE_ID = os.environ.get('TEST_COURSE_ID', u'edX/DemoX/Demo_Course')
DOC_BASE_URL = os.environ.get('DOC_BASE_URL', 'http://edx-insights.readthedocs.org/en/latest')

ENABLE_ENROLLMENT_MODES = str2bool(os.environ.get('ENABLE_ENROLLMENT_MODES', False))
ENABLE_FORUM_POSTS = str2bool(os.environ.get('ENABLE_FORUM_POSTS', False))

# Course API settings
ENABLE_COURSE_API = str2bool(os.environ.get('ENABLE_COURSE_API', False))
COURSE_API_URL = os.environ.get('COURSE_API_URL')
COURSE_API_KEY = os.environ.get('COURSE_API_KEY')

if ENABLE_COURSE_API and not (COURSE_API_URL and COURSE_API_KEY):
    raise Exception('Course API details not supplied!')
