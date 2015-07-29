"""
Tests for course analytics pages
"""

from bok_choy.page_object import PageObject
from acceptance_tests import TEST_COURSE_ID, DASHBOARD_SERVER_URL


class CoursePage(PageObject):
    basic_auth_username = None
    basic_auth_password = None

    def __init__(self, browser, course_id=None):
        # Create the path
        self.course_id = course_id or TEST_COURSE_ID
        path = 'courses/{}'.format(self.course_id)

        self.server_url = DASHBOARD_SERVER_URL
        self.page_url = '{0}/{1}'.format(self.server_url, path)

        # Call the constructor and setup the URL
        super(CoursePage, self).__init__(browser)

    def is_browser_on_page(self):
        return self.browser.current_url == self.page_url

    @property
    def url(self):
        return self.page_url


class CourseEnrollmentDemographicsPage(CoursePage):
    demographic = None

    def __init__(self, browser, course_id=None):
        super(CourseEnrollmentDemographicsPage, self).__init__(browser, course_id)
        self.page_url += '/enrollment/demographics/{0}/'.format(self.demographic)

    def is_browser_on_page(self):
        return (
            super(CourseEnrollmentDemographicsPage, self).is_browser_on_page()
            and 'Enrollment Demographics by {0}'.format(self.demographic.title())
            in self.browser.title
        )


class CourseEnrollmentDemographicsAgePage(CourseEnrollmentDemographicsPage):
    demographic = 'age'
