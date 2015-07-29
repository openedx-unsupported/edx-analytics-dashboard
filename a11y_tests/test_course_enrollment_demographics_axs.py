from bok_choy.web_app_test import WebAppTest
from a11y_tests.pages import CourseEnrollmentDemographicsAgePage
from a11y_tests.mixins import CoursePageTestsMixin

_multiprocess_can_split_ = True


class CourseEnrollmentDemographicsAgeTests(CoursePageTestsMixin, WebAppTest):
    """
    A test for the accessibility of the CourseEnrollmentDemographicsAgePage.
    """

    def setUp(self):
        super(CourseEnrollmentDemographicsAgeTests, self).setUp()
        self.page = CourseEnrollmentDemographicsAgePage(self.browser)

    def test_axs(self):
        # Log in and navigate to page
        self.login()
        self.page.visit()

        # Generate accessibillity report
        report = self.page.do_axs_audit()

        # Check that there was one page reviewed in this report
        self.assertEqual(1, len(report))
        result = report[0]

        # Verify that this page has no accessibility errors.
        self.assertEqual(0, len(result.errors))

        # Verify that this page currently has 2 accessibility warnings.
        self.assertEqual(2, len(result.warnings))

        # And that these are the warnings that the page currently gives.
        for warning in result.warnings:
            self.assertTrue(
                warning.startswith((
                    'Warning: AX_FOCUS_01',
                    'Warning: AX_COLOR_01',
                )),
                msg="Unexpected warning: {}".format(warning)
            )
