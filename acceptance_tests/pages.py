"""
Tests for course analytics pages
"""

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise

from acceptance_tests import (
    DASHBOARD_SERVER_URL, BASIC_AUTH_PASSWORD, BASIC_AUTH_USERNAME, LMS_HOSTNAME,
    TEST_COURSE_ID, TEST_GRADED_PROBLEM_ID, TEST_GRADED_PROBLEM_PART_ID, TEST_ASSIGNMENT_ID,
    TEST_ASSIGNMENT_TYPE, TEST_UNGRADED_SECTION_ID, TEST_UNGRADED_SUBSECTION_ID,
    TEST_UNGRADED_PROBLEM_ID, TEST_UNGRADED_PROBLEM_PART_ID, LMS_SSL_ENABLED,
    TEST_VIDEO_SECTION_ID, TEST_VIDEO_SUBSECTION_ID, TEST_VIDEO_ID)


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


class CourseEngagementVideosContentPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEngagementVideosContentPage, self).__init__(browser, course_id)
        self.page_url += '/engagement/videos/'

    def is_browser_on_page(self):
        return super(CourseEngagementVideosContentPage, self).is_browser_on_page() and \
               'Engagement Videos' in self.browser.title


class CourseEngagementVideoSectionPage(CoursePage):
    def __init__(self, browser, course_id=None, section_id=None):
        super(CourseEngagementVideoSectionPage, self).__init__(browser, course_id)
        self.section_id = section_id or TEST_VIDEO_SECTION_ID
        self.page_url += '/engagement/videos/sections/{}/'.format(self.section_id)

    def is_browser_on_page(self):
        return super(CourseEngagementVideoSectionPage, self).is_browser_on_page() and \
               'Engagement Videos' in self.browser.title


class CourseEngagementVideoSubsectionPage(CoursePage):
    def __init__(self, browser, course_id=None, section_id=None, subsection_id=None):
        super(CourseEngagementVideoSubsectionPage, self).__init__(browser, course_id)
        self.section_id = section_id or TEST_VIDEO_SECTION_ID
        self.subsection_id = subsection_id or TEST_VIDEO_SUBSECTION_ID
        self.page_url += '/engagement/videos/sections/{}/subsections/{}/'.format(
            self.section_id, self.subsection_id)

    def is_browser_on_page(self):
        return super(CourseEngagementVideoSubsectionPage, self).is_browser_on_page() and \
               'Engagement Videos' in self.browser.title


class CourseEngagementVideoTimelinePage(CoursePage):
    def __init__(self, browser, course_id=None, section_id=None, subsection_id=None, video_id=None):
        super(CourseEngagementVideoTimelinePage, self).__init__(browser, course_id)
        self.section_id = section_id or TEST_VIDEO_SECTION_ID
        self.subsection_id = subsection_id or TEST_VIDEO_SUBSECTION_ID
        self.video_id = video_id or TEST_VIDEO_ID
        self.page_url += '/engagement/videos/sections/{}/subsections/{}/modules/{}/timeline/'.format(
            self.section_id, self.subsection_id, self.video_id)

    def is_browser_on_page(self):
        return super(CourseEngagementVideoTimelinePage, self).is_browser_on_page() and \
               'Engagement Videos' in self.browser.title


class CourseIndexPage(DashboardPage):
    path = 'courses/'

    def __init__(self, browser):
        super(CourseIndexPage, self).__init__(browser)

    def is_browser_on_page(self):
        return self.browser.title.startswith('Courses')


class CoursePerformanceUngradedContentPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CoursePerformanceUngradedContentPage, self).__init__(browser, course_id)
        self.page_url += '/performance/ungraded_content/'

    def is_browser_on_page(self):
        return super(CoursePerformanceUngradedContentPage, self).is_browser_on_page() and \
               'Ungraded Problems' in self.browser.title


class CoursePerformanceUngradedSectionPage(CoursePage):
    def __init__(self, browser, course_id=None, section_id=None):
        super(CoursePerformanceUngradedSectionPage, self).__init__(browser, course_id)
        self.section_id = section_id or TEST_UNGRADED_SECTION_ID
        self.page_url += '/performance/ungraded_content/sections/{}/'.format(self.section_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceUngradedSectionPage, self).is_browser_on_page() and \
               'Ungraded Problems' in self.browser.title


class CoursePerformanceUngradedSubsectionPage(CoursePage):
    def __init__(self, browser, course_id=None, section_id=None, subsection_id=None):
        super(CoursePerformanceUngradedSubsectionPage, self).__init__(browser, course_id)
        self.section_id = section_id or TEST_UNGRADED_SECTION_ID
        self.subsection_id = subsection_id or TEST_UNGRADED_SUBSECTION_ID
        self.page_url += '/performance/ungraded_content/sections/{}/subsections/{}/'.format(
            self.section_id, self.subsection_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceUngradedSubsectionPage, self).is_browser_on_page() and \
               'Ungraded Problems' in self.browser.title


class CoursePerformanceUngradedAnswerDistributionPage(CoursePage):
    def __init__(self, browser, course_id=None, section_id=None, subsection_id=None, problem_id=None, part_id=None):
        super(CoursePerformanceUngradedAnswerDistributionPage, self).__init__(browser, course_id)
        self.section_id = section_id or TEST_UNGRADED_SECTION_ID
        self.subsection_id = subsection_id or TEST_UNGRADED_SUBSECTION_ID
        self.problem_id = problem_id or TEST_UNGRADED_PROBLEM_ID
        self.part_id = part_id or TEST_UNGRADED_PROBLEM_PART_ID
        self.page_url += '/performance/ungraded_content/sections/{}/subsections/{}/problems/{}/' \
                         'parts/{}/answer_distribution/'.format(self.section_id, self.subsection_id,
                                                                self.problem_id, self.part_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceUngradedAnswerDistributionPage, self).is_browser_on_page() and \
               self.browser.title.startswith('Performance: Problem Submissions')


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
        self.page_url += '/performance/graded_content/{}/'.format(self.assignment_type)

    def is_browser_on_page(self):
        return super(CoursePerformanceGradedContentByTypePage, self).is_browser_on_page() and \
               self.assignment_type in self.browser.title


class CoursePerformanceAssignmentPage(CoursePage):
    def __init__(self, browser, course_id=None, assignment_id=None):
        super(CoursePerformanceAssignmentPage, self).__init__(browser, course_id)
        self.assignment_id = assignment_id or TEST_ASSIGNMENT_ID
        self.page_url += '/performance/graded_content/assignments/{}/'.format(self.assignment_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceAssignmentPage, self).is_browser_on_page() and \
               'Graded Content' in self.browser.title


class CoursePerformanceAnswerDistributionPage(CoursePage):
    def __init__(self, browser, course_id=None, assignment_id=None, problem_id=None, part_id=None):
        super(CoursePerformanceAnswerDistributionPage, self).__init__(browser, course_id)
        self.assignment_id = assignment_id or TEST_ASSIGNMENT_ID
        self.problem_id = problem_id or TEST_GRADED_PROBLEM_ID
        self.part_id = part_id or TEST_GRADED_PROBLEM_PART_ID
        self.page_url += '/performance/graded_content/assignments/{}/problems/{}/parts/{}/answer_distribution/'.format(
            self.assignment_id, self.problem_id, self.part_id)

    def is_browser_on_page(self):
        return super(CoursePerformanceAnswerDistributionPage, self).is_browser_on_page() and \
               self.browser.title.startswith('Performance: Problem Submissions')


class CourseLearnersPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseLearnersPage, self).__init__(browser, course_id)
        self.page_url += '/learners/'

    def is_browser_on_page(self):
        return super(CourseLearnersPage, self).is_browser_on_page() \
            and self.browser.title.startswith('Learners')


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


class ServiceUnavailableErrorPage(ErrorPage):
    error_code = 503
    error_title = u"We're having trouble loading this page. Please try again in a minute."
