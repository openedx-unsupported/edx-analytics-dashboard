"""
Tests for course analytics pages
"""

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise

from acceptance_tests import DASHBOARD_SERVER_URL, BASIC_AUTH_PASSWORD, BASIC_AUTH_USERNAME, LMS_HOSTNAME, \
    TEST_COURSE_ID, TEST_PROBLEM_ID, TEST_PROBLEM_PART_ID, TEST_ASSIGNMENT_ID, TEST_ASSIGNMENT_TYPE, \
    LMS_SSL_ENABLED


class DashboardPage(PageObject):  # pylint: disable=abstract-method
    path = None
    basic_auth_username = None
    basic_auth_password = None

    @property
    def url(self):
        return self.page_url

    def __init__(self, browser, path=None):
        super(DashboardPage, self).__init__(browser)
        path = path or self.path
        self.server_url = DASHBOARD_SERVER_URL
        self.page_url = '{0}/{1}'.format(self.server_url, path)


class LandingPage(DashboardPage):
    path = ''

    def __init__(self, browser):
        super(LandingPage, self).__init__(browser)

    def is_browser_on_page(self):
        return self.browser.current_url == self.page_url


class CoursePage(DashboardPage):
    def __init__(self, browser, course_id=None):
        # Create the path
        self.course_id = course_id or TEST_COURSE_ID
        path = 'courses/{}'.format(self.course_id)

        # Call the constructor and setup the URL
        super(CoursePage, self).__init__(browser, path)

    def is_browser_on_page(self):
        return self.browser.current_url == self.page_url


class CourseHomePage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseHomePage, self).__init__(browser, course_id)
        self.page_url += '/'

    def is_browser_on_page(self):
        return super(CourseHomePage, self).is_browser_on_page() and self.browser.title.startswith('Course Home')


class CourseEnrollmentActivityPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentActivityPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/activity/'

    def is_browser_on_page(self):
        return super(CourseEnrollmentActivityPage, self).is_browser_on_page() and \
               'Enrollment Activity' in self.browser.title


class LMSLoginPage(PageObject):
    @property
    def url(self):
        protocol = 'https' if LMS_SSL_ENABLED else 'http'

        if BASIC_AUTH_USERNAME and BASIC_AUTH_PASSWORD:
            return '{0}://{1}:{2}@{3}/login'.format(protocol, BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD, LMS_HOSTNAME)

        return '{0}://{1}/login'.format(protocol, LMS_HOSTNAME)

    def is_browser_on_page(self):
        return self.browser.title.startswith('Log into')

    def _is_browser_on_lms_dashboard(self):
        return lambda: self.browser.title.startswith('Dashboard')

    def login(self, username, password):
        self.q(css='input#email').fill(username)
        self.q(css='input#password').fill(password)
        self.q(css='button#submit').click()

        # Wait for LMS to redirect to the dashboard
        EmptyPromise(self._is_browser_on_lms_dashboard(), "LMS login redirected to dashboard").fulfill()


class LoginPage(DashboardPage):
    path = 'accounts/login'

    def is_browser_on_page(self):
        return True


class CourseEnrollmentDemographicsPage(CoursePage):
    demographic = None

    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentDemographicsPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/demographics/{0}/'.format(self.demographic)

    def is_browser_on_page(self):
        return super(CourseEnrollmentDemographicsPage, self).is_browser_on_page() and \
               'Enrollment Demographics by {0}'.format(self.demographic.title()) in self.browser.title


class CourseEnrollmentDemographicsAgePage(CourseEnrollmentDemographicsPage):
    demographic = 'age'


class CourseEnrollmentDemographicsGenderPage(CourseEnrollmentDemographicsPage):
    demographic = 'gender'


class CourseEnrollmentDemographicsEducationPage(CourseEnrollmentDemographicsPage):
    demographic = 'education'


class CourseEnrollmentGeographyPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentGeographyPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/geography/'

    def is_browser_on_page(self):
        return super(CourseEnrollmentGeographyPage, self).is_browser_on_page() and \
               'Enrollment Geography' in self.browser.title


class CourseEngagementContentPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEngagementContentPage, self).__init__(browser, course_id)
        self.page_url += '/engagement/content/'

    def is_browser_on_page(self):
        return super(CourseEngagementContentPage, self).is_browser_on_page() and \
               'Engagement Content' in self.browser.title


class CourseIndexPage(DashboardPage):
    path = 'courses/'

    def __init__(self, browser):
        super(CourseIndexPage, self).__init__(browser)

    def is_browser_on_page(self):
        return self.browser.title.startswith('Courses')


class CoursePerformanceGradedContentPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CoursePerformanceGradedContentPage, self).__init__(browser, course_id)
        self.page_url += '/performance/graded_content/'

    def is_browser_on_page(self):
        return super(CoursePerformanceGradedContentPage, self).is_browser_on_page() and \
               'Graded Content' in self.browser.title


class CoursePerformanceGradedContentByTypePage(CoursePage):
    def __init__(self, browser, course_id=None, assignment_type=None):
        super(CoursePerformanceGradedContentByTypePage, self).__init__(browser, course_id)
        self.assignment_type = assignment_type or TEST_ASSIGNMENT_TYPE
        self.page_url = '{}/performance/graded_content/{}/'.format(self.page_url, self.assignment_type)

    def is_browser_on_page(self):
        return super(CoursePerformanceGradedContentByTypePage, self).is_browser_on_page() and \
               self.assignment_type in self.browser.title


class CoursePerformanceAssignmentPage(CoursePage):
    def __init__(self, browser, course_id=None, assignment_id=None):
        super(CoursePerformanceAssignmentPage, self).__init__(browser, course_id)
        self.assignment_id = assignment_id or TEST_ASSIGNMENT_ID
        self.page_url = '{}/performance/graded_content/assignments/{}/'.format(self.page_url, self.assignment_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceAssignmentPage, self).is_browser_on_page() and \
               'Graded Content' in self.browser.title


class CoursePerformanceAnswerDistributionPage(CoursePage):
    def __init__(self, browser, course_id=None, assignment_id=None, problem_id=None, part_id=None):
        super(CoursePerformanceAnswerDistributionPage, self).__init__(browser, course_id)
        self.assignment_id = assignment_id or TEST_ASSIGNMENT_ID
        self.problem_id = problem_id or TEST_PROBLEM_ID
        self.part_id = part_id or TEST_PROBLEM_PART_ID
        self.page_url += '/performance/graded_content/assignments/{}/problems/{}/parts/{}/answer_distribution/'.format(
            self.assignment_id, self.problem_id, self.part_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceAnswerDistributionPage, self).is_browser_on_page() and \
               self.browser.title.startswith('Performance: Problem Submissions')


class ErrorPage(DashboardPage):
    error_code = None
    error_title = None

    def __init__(self, browser):
        self.path = self.path or '{}/'.format(self.error_code)
        super(ErrorPage, self).__init__(browser)

    def is_browser_on_page(self):
        element = self.q(css='.error-title')
        return element.present and element.text[0] == self.error_title


class ServerErrorPage(ErrorPage):
    error_code = 500
    error_title = u'An Error Occurred'


class NotFoundErrorPage(ErrorPage):
    error_code = 404
    error_title = u'Page Not Found'


class AccessDeniedErrorPage(ErrorPage):
    error_code = 403
    error_title = u'Access Denied'


class BadGatewayErrorPage(ErrorPage):
    error_code = 502
    error_title = u"We're having trouble loading this page. Please try again in a minute."
