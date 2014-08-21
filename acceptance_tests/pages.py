"""
Tests for course analytics pages
"""

from bok_choy.page_object import PageObject

from acceptance_tests import DASHBOARD_SERVER_URL, auto_auth


class DashboardPage(PageObject):
    path = None

    @property
    def url(self):
        return self.page_url

    def __init__(self, browser, path=None):
        super(DashboardPage, self).__init__(browser)
        path = path or self.path
        self.server_url = DASHBOARD_SERVER_URL
        self.page_url = '{0}/{1}'.format(self.server_url, path)


class CoursePage(DashboardPage):
    def __init__(self, browser, course_id=None):
        # Create the path
        self.course_id = course_id or 'edX/DemoX/Demo_Course'
        path = 'courses/{}'.format(self.course_id)

        # Call the constructor and setup the URL
        super(CoursePage, self).__init__(browser, path)

        # Automatically create and login a new user
        auto_auth(browser, self.server_url)

    def is_browser_on_page(self):
        return self.browser.current_url == self.page_url


class CourseEnrollmentActivityPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentActivityPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/activity/'

    def is_browser_on_page(self):
        return super(CourseEnrollmentActivityPage, self).is_browser_on_page() and 'Enrollment Activity' in self.browser.title


class LoginPage(DashboardPage):
    path = 'accounts/login'

    def is_browser_on_page(self):
        return True


class LogoutPage(DashboardPage):
    path = 'accounts/logout'

    def is_browser_on_page(self):
        return self.browser.title.startswith('Logged Out')


class CourseEnrollmentGeographyPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentGeographyPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/geography/'

    def is_browser_on_page(self):
        return super(CourseEnrollmentGeographyPage, self).is_browser_on_page() and 'Enrollment Geography' in self.browser.title


class CourseEngagementContentPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEngagementContentPage, self).__init__(browser, course_id)
        self.page_url += '/engagement/content/'

    def is_browser_on_page(self):
        return super(CourseEngagementContentPage, self).is_browser_on_page() and 'Engagement Content' in self.browser.title


class CourseIndexPage(DashboardPage):
    path = 'courses/'

    def __init__(self, browser):
        super(CourseIndexPage, self).__init__(browser)

        # Automatically create and login a new user
        auto_auth(browser, self.server_url)

    def is_browser_on_page(self):
        return 'Courses' in self.browser.title
