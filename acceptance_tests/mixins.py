import locale
from bok_choy.promise import EmptyPromise
from analyticsclient.client import Client
from acceptance_tests import API_SERVER_URL, API_AUTH_TOKEN, DASHBOARD_FEEDBACK_EMAIL, SUPPORT_URL, LMS_USERNAME, \
    LMS_PASSWORD, DASHBOARD_SERVER_URL, ENABLE_AUTO_AUTH
from pages import LMSLoginPage


MAX_SUMMARY_POINT_VALUE_LENGTH = 13


class AnalyticsApiClientMixin(object):
    api_client = None

    def setUp(self):
        super(AnalyticsApiClientMixin, self).setUp()

        api_url = API_SERVER_URL
        auth_token = API_AUTH_TOKEN
        self.api_client = Client(api_url, auth_token=auth_token, timeout=5)


class AssertMixin(object):
    """ Shared asserts for convenience """

    def assertValidHref(self, selector):
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertNotEqual(element.attrs('href')[0], '#')

    def assertTableColumnHeadingsEqual(self, table_selector, headings):
        rows = self.page.q(css=('%s thead th' % table_selector))
        self.assertTrue(rows.present)
        self.assertListEqual(rows.text, headings)

    def assertElementHasContent(self, css):
        element = self.page.q(css=css)
        self.assertTrue(element.present)
        html = element.html[0]
        self.assertIsNotNone(html)
        self.assertNotEqual(html, '')

    def assertValidFeedbackLink(self, selector):
        # check that we have an email
        element = self.page.q(css=selector)
        self.assertEqual(element.text[0], DASHBOARD_FEEDBACK_EMAIL)


class FooterMixin(AssertMixin):
    def _test_footer(self):
        # make sure we have the footer
        footer_selector = "footer[class=footer]"
        element = self.page.q(css=footer_selector)
        self.assertTrue(element.present)

        # check that we have an email
        self.assertValidFeedbackLink(footer_selector + " a[class=feedback-email]")

        # check that we have the support link
        selector = footer_selector + " a[class=support-link]"
        element = self.page.q(css=selector)
        self.assertEqual(element.attrs('href')[0], SUPPORT_URL)

        # Verify the terms of service link is present
        selector = footer_selector + " a[data-role=tos]"
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], u'Terms of Service')

        # Verify the privacy policy link is present
        selector = footer_selector + " a[data-role=privacy-policy]"
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], u'Privacy Policy')


class PrimaryNavMixin(object):
    def _test_user_menu(self):
        """
        Verify the user menu functions properly.
        """
        element = self.page.q(css='a.active-user.dropdown-toggle')
        self.assertTrue(element.present)
        self.assertEqual(element.attrs('aria-expanded')[0], 'false')

        element.click()

        # Ensure the menu is actually visible onscreen
        element = self.page.q(css='ul.dropdown-menu.active-user-nav')
        self.assertTrue(element.visible)


class LoginMixin(object):
    def setUp(self):
        super(LoginMixin, self).setUp()
        self.lms_login_page = LMSLoginPage(self.browser)

    def login(self):
        if ENABLE_AUTO_AUTH:
            self.login_with_auto_auth()
        else:
            self.login_with_lms()

    def login_with_auto_auth(self):
        url = '{}/test/auto_auth/'.format(DASHBOARD_SERVER_URL)
        self.browser.get(url)

    def login_with_lms(self):
        """ Visit LMS and login. """

        # Note: We use Selenium directly here (as opposed to Bok Choy) to avoid issues with promises being broken.
        self.lms_login_page.browser.get(self.lms_login_page.url)
        self.lms_login_page.login(LMS_USERNAME, LMS_PASSWORD)


class CoursePageTestsMixin(LoginMixin, AnalyticsApiClientMixin, FooterMixin, PrimaryNavMixin):
    """ Mixin for common course page assertions and tests. """

    DASHBOARD_DATE_FORMAT = '%B %d, %Y'
    page = None

    def setUp(self):
        super(CoursePageTestsMixin, self).setUp()
        self.api_date_format = self.api_client.DATE_FORMAT
        self.api_datetime_format = self.api_client.DATETIME_FORMAT

    def assertSummaryPointValueEquals(self, data_selector, value):
        """
        Compares the value in the summary card the "value" argument.

        Arguments:
            data_selector (String): Attribute selector (ex. data-stat-type=current_enrollment)
            tip_text (String): expected value
        """
        # Account for Django truncation
        if len(value) > MAX_SUMMARY_POINT_VALUE_LENGTH:
            value = value[:(MAX_SUMMARY_POINT_VALUE_LENGTH - 3)] + '...'

        element = self.page.q(css="div[{0}] .summary-point-number".format(data_selector))
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], value)

    def assertSummaryTooltipEquals(self, data_selector, tip_text):
        """
        Compares the tooltip in the summary card the "tip_text" argument.

        Arguments:
            data_selector (String): Attribute selector (ex. data-stat-type=current_enrollment)
            tip_text (String): expected text
        """
        help_selector = "div[{0}] .summary-point-help".format(data_selector)
        element = self.page.q(css=help_selector)
        self.assertTrue(element.present)

        # check to see if
        screen_reader_element = self.page.q(css=help_selector + " > span[class=sr-only]")
        self.assertTrue(screen_reader_element.present)
        self.assertEqual(screen_reader_element.text[0], tip_text)

        tooltip_element = self.page.q(css=help_selector + " > i[data-toggle='tooltip']")
        self.assertTrue(tooltip_element.present)
        # the context of title gets move to "data-original-title"
        self.assertEqual(tooltip_element[0].get_attribute('data-original-title'), tip_text)

    def assertDataUpdateMessageEquals(self, value):
        element = self.page.q(css='div.data-update-message')
        self.assertEqual(element.text[0], value)

    def format_time_as_dashboard(self, value):
        return value.strftime(self.DASHBOARD_DATE_FORMAT)

    def _format_last_updated_time(self, d):
        return d.strftime('%I:%M %p').lstrip('0')

    def format_last_updated_date_and_time(self, d):
        return {'update_date': d.strftime(self.DASHBOARD_DATE_FORMAT), 'update_time': self._format_last_updated_time(d)}

    def fulfill_loading_promise(self, css_selector):
        """
        Ensure the info contained by `css_selector` is loaded via AJAX.

        Arguments
            css_selector (string)   --  CSS selector of the parent element that will contain the loading message.
        """

        EmptyPromise(
            lambda: 'Loading...' not in self.page.q(css=css_selector + ' .loading-container').text,
            "Loading finished."
        ).fulfill()

    def _get_data_update_message(self):
        raise NotImplementedError

    def _test_data_update_message(self):
        """ Validate the content in the data update message container. """

        message = self._get_data_update_message()
        self.assertDataUpdateMessageEquals(message)

    def test_page(self):
        """
        Primary test method.

        Sub-classes should override this method and add additional tests. Sub-classes can safely assume that, if tests
        pass, execution of this parent method will leave the browser on the page being tested.
        :return:
        """
        self.login()
        self.page.visit()
        self._test_user_menu()
        self._test_footer()
        self._test_data_update_message()

    @staticmethod
    def format_number(value):
        """ Format the given value for the current locale (e.g. include decimal separator). """
        return locale.format("%d", value, grouping=True)
