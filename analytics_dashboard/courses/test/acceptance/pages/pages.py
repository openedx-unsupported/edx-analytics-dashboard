"""
Tests for course analytics pages
"""

from bok_choy.page_object import PageObject
import re

class EnrollmentPage(PageObject):

    # this will be set in the constructor for navigating to the correct page
    url = None

    def __init__(self, browser, baseUrl):
        # call the parent to set the browser
        super(EnrollmentPage, self).__init__(browser)
        self.url = baseUrl + '/courses/1234/enrollment/'

    # this method extends the parent method to ensure that we're on the
    # correct page
    def is_browser_on_page(self):
        title = self.browser.title
        matches = re.match(u'^Enrollment .+$', title)
        return matches is not None


