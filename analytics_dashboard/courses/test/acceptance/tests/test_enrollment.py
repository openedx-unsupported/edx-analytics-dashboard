from django.conf import settings

import unittest
from bok_choy.web_app_test import WebAppTest
from acceptance.pages.pages import EnrollmentPage

class TestEnrollment(WebAppTest):
    """
    Tests for the Enrollment page.
    """

    def setUp(self):
        """
        Instantiate the page object.
        """
        super(TestEnrollment, self).setUp()

        baseUrl = 'http://{address}:{port}'.format(address=settings.ACCEPTANCE_TEST_SERVER['address'],
                                                   port=settings.ACCEPTANCE_TEST_SERVER['port'])

        self.enrollment_page = EnrollmentPage(self.browser, baseUrl)

    def test_enrollment_page_exists(self):
        """
        Make sure that the enrollment page is accessible.
        """
        self.enrollment_page.visit()