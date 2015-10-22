from unittest import skipUnless

from bok_choy.web_app_test import WebAppTest

from acceptance_tests import PLATFORM_NAME, APPLICATION_NAME, SUPPORT_EMAIL, ENABLE_ERROR_PAGE_TESTS
from acceptance_tests.pages import ServerErrorPage, NotFoundErrorPage, AccessDeniedErrorPage, \
    ServiceUnavailableErrorPage


@skipUnless(ENABLE_ERROR_PAGE_TESTS, 'Error page tests are not enabled.')
class ErrorPagesTests(WebAppTest):
    error_page_classes = [ServerErrorPage, NotFoundErrorPage, AccessDeniedErrorPage, ServiceUnavailableErrorPage]

    def test_valid_pages(self):
        for page_class in self.error_page_classes:
            page = page_class(self.browser)

            # Visit the page
            page.visit()

            # Check the title
            expected = u'{0} | {1} {2}'.format(page.error_title, PLATFORM_NAME, APPLICATION_NAME)
            self.assertEqual(expected, self.browser.title)

            # Check the support link
            element = page.q(css='a[data-role=support-email]')
            self.assertTrue(element.present)
            href = element.attrs('href')[0]
            self.assertEqual(href, 'mailto:{}'.format(SUPPORT_EMAIL))
