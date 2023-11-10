"""
Tests for course analytics pages
"""


from acceptance_tests import DASHBOARD_SERVER_URL, TEST_COURSE_ID


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
