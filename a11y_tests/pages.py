"""
Tests for course analytics pages
"""


from bok_choy.page_object import PageObject

from acceptance_tests import DASHBOARD_SERVER_URL, TEST_COURSE_ID


class CoursePage(PageObject):
    basic_auth_username = None
    basic_auth_password = None

    def __init__(self, browser, course_id=None):
        # Create the path
        self.course_id = course_id or TEST_COURSE_ID
        path = f'courses/{self.course_id}'

        self.server_url = DASHBOARD_SERVER_URL
        self.page_url = f'{self.server_url}/{path}'

        # Call the constructor and setup the URL
        super().__init__(browser)

    def is_browser_on_page(self):
        return self.browser.current_url == self.page_url

    @property
    def url(self):
        return self.page_url


class CourseEnrollmentDemographicsPage(CoursePage):
    demographic = None

    def __init__(self, browser, course_id=None):
        super().__init__(browser, course_id)
        self.page_url += f'/enrollment/demographics/{self.demographic}/'

    def is_browser_on_page(self):
        return (
            super().is_browser_on_page()
            and f'Enrollment Demographics by {self.demographic.title()}'
            in self.browser.title
        )


class CourseEnrollmentDemographicsAgePage(CourseEnrollmentDemographicsPage):
    demographic = 'age'
