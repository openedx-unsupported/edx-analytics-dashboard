from a11y_tests.mixins import CoursePageTestsMixin
from a11y_tests.pages import CourseEnrollmentDemographicsAgePage
from bok_choy.promise import EmptyPromise
from bok_choy.web_app_test import WebAppTest

_multiprocess_can_split_ = True


class CourseEnrollmentDemographicsAgeTests(CoursePageTestsMixin, WebAppTest):
    """
    A test for the accessibility of the CourseEnrollmentDemographicsAgePage.
    """

    def setUp(self):
        super(CourseEnrollmentDemographicsAgeTests, self).setUp()
        self.page = CourseEnrollmentDemographicsAgePage(self.browser)

    def test_a11y(self):
        # Log in and navigate to page
        self.login()
        self.page.visit()

        self.page.a11y_audit.config.set_rules({
            "ignore": [
                'color-contrast',  # TODO: AN-6010, AN-6011
                'skip-link',  # TODO: AN-6185
                'link-href',  # TODO: AN-6186
                'icon-aria-hidden',  # TODO: AN-6187
            ],
        })

        # Wait for the datatable to finish loading
        ready_promise = EmptyPromise(
            lambda: 'Loading' not in self.page.q(css='div.section-data-table').text,
            "Page finished loading"
        ).fulfill()

        # Check the page for accessibility errors
        report = self.page.a11y_audit.check_for_accessibility_errors()
