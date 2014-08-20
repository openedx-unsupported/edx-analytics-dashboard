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


class CourseEnrollmentPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/'

    def is_browser_on_page(self):
        return super(CourseEnrollmentPage, self).is_browser_on_page() and 'Enrollment' in self.browser.title


class CourseEngagementPage(CoursePage):
    def __init__(self, browser, course_id=None):
        super(CourseEngagementPage, self).__init__(browser, course_id)
        self.page_url += '/engagement/'

    def is_browser_on_page(self):
        return super(CourseEngagementPage, self).is_browser_on_page() and 'Engagement' in self.browser.title


class LoginPage(DashboardPage):
    path = 'accounts/login'

    def is_browser_on_page(self):
        return True


class LogoutPage(DashboardPage):
    path = 'accounts/logout'

    def is_browser_on_page(self):
        return self.browser.title.startswith('Logged Out')
