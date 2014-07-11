"""
Tests for course analytics pages
"""

from bok_choy.page_object import PageObject

from acceptance_tests import DASHBOARD_SERVER_URL


class CoursePage(PageObject):
    @property
    def url(self):
        return self.page_url

    def __init__(self, browser, course_id=None, server_url=None):
        super(CoursePage, self).__init__(browser)

        server_url = server_url or DASHBOARD_SERVER_URL
        self.course_id = course_id or 'edX/DemoX/Demo_Course'
        self.page_url = '{0}/courses/{1}'.format(server_url, self.course_id)

    def is_browser_on_page(self):
        return self.browser.current_url == self.page_url


class CourseEnrollmentPage(CoursePage):
    def __init__(self, browser, course_id=None, server_url=None):
        super(CourseEnrollmentPage, self).__init__(browser, course_id, server_url)
        self.page_url += '/enrollment/'

    def is_browser_on_page(self):
        return super(CourseEnrollmentPage, self).is_browser_on_page() and 'Enrollment' in self.browser.title


class CourseEngagementPage(CoursePage):
    def __init__(self, browser, course_id=None, server_url=None):
        super(CourseEngagementPage, self).__init__(browser, course_id, server_url)
        self.page_url += '/engagement/'

    def is_browser_on_page(self):
        return super(CourseEngagementPage, self).is_browser_on_page() and 'Engagement' in self.browser.title
