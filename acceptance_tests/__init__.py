import locale
import os

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def str2bool(s):
    s = unicode(s)
    return s.lower() in (u"yes", u"true", u"t", u"1")

# Dashboard settings
DASHBOARD_SERVER_URL = os.environ.get('DASHBOARD_SERVER_URL', 'http://localhost:9000')
DASHBOARD_FEEDBACK_EMAIL = os.environ.get('DASHBOARD_FEEDBACK_EMAIL', 'override.this.email@example.com')
PLATFORM_NAME = os.environ.get('PLATFORM_NAME', 'Open edX')
APPLICATION_NAME = os.environ.get('APPLICATION_NAME', 'Insights')
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@example.com')
OPEN_SOURCE_URL = os.environ.get('OPEN_SOURCE_URL', 'http://example.com/')
RESEARCH_URL = os.environ.get('RESEARCH_URL', 'http://example.com/')
SHOW_LANDING_RESEARCH = str2bool(os.environ.get('SHOW_LANDING_RESEARCH', True))

# Analytics data API settings
API_SERVER_URL = os.environ['API_SERVER_URL']
API_AUTH_TOKEN = os.environ['API_AUTH_TOKEN']

# Test configuration
ENABLE_AUTO_AUTH = str2bool(os.environ.get('ENABLE_AUTO_AUTH', False))
ENABLE_OAUTH_TESTS = str2bool(os.environ.get('ENABLE_OAUTH_TESTS', True))
ENABLE_ERROR_PAGE_TESTS = str2bool(os.environ.get('ENABLE_ERROR_PAGE_TESTS', True))

# LMS settings
BASIC_AUTH_USERNAME = os.environ.get('BASIC_AUTH_USERNAME')
BASIC_AUTH_PASSWORD = os.environ.get('BASIC_AUTH_PASSWORD')
LMS_HOSTNAME = os.environ.get('LMS_HOSTNAME')
LMS_USERNAME = os.environ.get('LMS_USERNAME')
LMS_PASSWORD = os.environ.get('LMS_PASSWORD')
LMS_SSL_ENABLED = str2bool(os.environ.get('LMS_SSL_ENABLED', True))

if ENABLE_OAUTH_TESTS and not (LMS_HOSTNAME and LMS_USERNAME and LMS_PASSWORD):
    raise Exception('LMS settings must be set in order to test OAuth.')

TEST_COURSE_ID = os.environ.get('TEST_COURSE_ID', u'edX/DemoX/Demo_Course')
TEST_ASSIGNMENT_TYPE = os.environ.get('TEST_ASSIGNMENT_TYPE', 'Homework')
TEST_ASSIGNMENT_ID = os.environ.get('TEST_ASSIGNMENT_ID', u'i4x://edX/DemoX/sequential/basic_questions')
TEST_GRADED_PROBLEM_ID = os.environ.get('TEST_GRADED_PROBLEM_ID',
                                        u'i4x://edX/DemoX/problem/a0effb954cca4759994f1ac9e9434bf4')
TEST_GRADED_PROBLEM_PART_ID = os.environ.get('TEST_GRADED_PROBLEM_PART_ID',
                                             u'i4x-edX-DemoX-problem-a0effb954cca4759994f1ac9e9434bf4_2_1')
TEST_UNGRADED_SECTION_ID = os.environ.get('TEST_UNGRADED_SECTION_ID',
                                          u'i4x://edX/DemoX/chapter/interactive_demonstrations')
TEST_UNGRADED_SUBSECTION_ID = os.environ.get('TEST_UNGRADED_SUBSECTION_ID',
                                             u'i4x://edX/DemoX/sequential/19a30717eff543078a5d94ae9d6c18a5')
TEST_UNGRADED_PROBLEM_ID = os.environ.get('TEST_UNGRADED_PROBLEM_ID',
                                          u'i4x://edX/DemoX/problem/303034da25524878a2e66fb57c91cf85')
TEST_UNGRADED_PROBLEM_PART_ID = os.environ.get('TEST_UNGRADED_PROBLEM_PART_ID',
                                               u'i4x-edX-DemoX-problem-303034da25524878a2e66fb57c91cf85_2_1')
TEST_VIDEO_SECTION_ID = os.environ.get('TEST_VIDEO_SECTION_ID',
                                       u'i4x://edX/DemoX/chapter/interactive_demonstrations')
TEST_VIDEO_SUBSECTION_ID = os.environ.get('TEST_VIDEO_SUBSECTION_ID',
                                          u'i4x://edX/DemoX/sequential/19a30717eff543078a5d94ae9d6c18a5')
TEST_VIDEO_ID = os.environ.get('TEST_VIDEO_ID',
                               u'i4x://edX/DemoX/video/7e9b434e6de3435ab99bd3fb25bde807')

DOC_BASE_URL = os.environ.get('DOC_BASE_URL', 'http://edx-insights.readthedocs.org/en/latest')

ENABLE_ENROLLMENT_MODES = str2bool(os.environ.get('ENABLE_ENROLLMENT_MODES', False))
ENABLE_FORUM_POSTS = str2bool(os.environ.get('ENABLE_FORUM_POSTS', False))

# Course API settings
ENABLE_COURSE_API = str2bool(os.environ.get('ENABLE_COURSE_API', False))
COURSE_API_URL = os.environ.get('COURSE_API_URL')
COURSE_API_KEY = os.environ.get('COURSE_API_KEY')

if ENABLE_COURSE_API and not (COURSE_API_URL and COURSE_API_KEY):
    raise Exception('Course API details not supplied!')

# Video preview
ENABLE_VIDEO_PREVIEW = str2bool(os.environ.get('ENABLE_VIDEO_PREVIEW', False))

# Learner analytics
ENABLE_LEARNER_ANALYTICS = str2bool(os.environ.get('ENABLE_LEARNER_ANALYTICS', False))
