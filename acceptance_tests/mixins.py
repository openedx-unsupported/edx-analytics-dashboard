import datetime
import locale
from unittest import skip

from bok_choy.promise import EmptyPromise
from selenium.webdriver.common.keys import Keys

from acceptance_tests import (
    API_AUTH_TOKEN,
    API_SERVER_URL,
    COURSE_API_KEY,
    COURSE_API_URL,
    DASHBOARD_FEEDBACK_EMAIL,
    DASHBOARD_SERVER_URL,
    DOC_BASE_URL,
    ENABLE_AUTO_AUTH,
    ENABLE_COURSE_API,
    LMS_PASSWORD,
    LMS_USERNAME,
    SOAPBOX_GLOBAL_MESSAGE,
    SOAPBOX_INACTIVE_MESSAGE,
    SOAPBOX_SINGLE_PAGE_MESSAGE,
    SOAPBOX_SINGLE_PAGE_PATH,
    SUPPORT_EMAIL,
)
from acceptance_tests.pages import LMSLoginPage
from analyticsclient.client import Client
from common.clients import CourseStructureApiClient


MAX_SUMMARY_POINT_VALUE_LENGTH = 13


class AnalyticsApiClientMixin(object):
    analytics_api_client = None

    def setUp(self):
        super(AnalyticsApiClientMixin, self).setUp()

        api_url = API_SERVER_URL
        auth_token = API_AUTH_TOKEN
        self.analytics_api_client = Client(api_url, auth_token=auth_token, timeout=10)


class CourseApiMixin(object):
    course_api_client = None

    def setUp(self):
        super(CourseApiMixin, self).setUp()

        if ENABLE_COURSE_API:
            self.course_api_client = CourseStructureApiClient(COURSE_API_URL, COURSE_API_KEY, 5)

    def get_course_name_or_id(self, course_id):
        """ Returns the course name if the course API is enabled; otherwise, the course ID. """
        course_name = course_id
        if ENABLE_COURSE_API:
            course_name = self.course_api_client.courses(course_id).get()['name']

        return course_name


class AssertMixin(object):
    """ Shared asserts for convenience """

    def assertValidHref(self, selector):
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertNotEqual(element.attrs('href')[0], '#')

    def assertHrefEqual(self, selector, href):
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.attrs('href')[0], href)

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

    def assertTable(self, table_selector, columns, download_selector=None):
        # Ensure the table is loaded via AJAX
        self.fulfill_loading_promise(table_selector)

        # make sure the containing element is present
        element = self.page.q(css=table_selector)
        self.assertTrue(element.present)

        # make sure the table is present
        table_selector += " table"
        element = self.page.q(css=table_selector)
        self.assertTrue(element.present)

        # check the headings
        self.assertTableColumnHeadingsEqual(table_selector, columns)

        rows = self.page.browser.find_elements_by_css_selector('{} tbody tr'.format(table_selector))
        self.assertGreater(len(rows), 0)

        if download_selector is not None:
            self.assertValidHref(download_selector)

    def assertRowTextEquals(self, cols, expected_texts):
        """
        Asserts that the given columns contain the expected text.
        :param cols: Array of Selenium HTML elements.
        :param expected_texts: Array of strings.
        """
        actual = [col.text for col in cols]
        self.assertListEqual(actual, expected_texts)


class PageTestMixin(object):
    def test_page(self):
        pass


class FooterMixin(AssertMixin):
    footer_selector = "footer[class=footer]"

    def _test_footer(self):
        # make sure we have the footer
        element = self.page.q(css=self.footer_selector)
        self.assertTrue(element.present)

    def test_page(self):
        super(FooterMixin, self).test_page()
        self._test_footer()


class FooterLegalMixin(FooterMixin):
    def _test_footer(self):
        super(FooterLegalMixin, self)._test_footer()

        # Verify the terms of service link is present
        selector = self.footer_selector + " a[data-role=tos]"
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], u'Terms of Service')

        # Verify the privacy policy link is present
        selector = self.footer_selector + " a[data-role=privacy-policy]"
        element = self.page.q(css=selector)
        self.assertTrue(element.present)
        self.assertEqual(element.text[0], u'Privacy Policy')


class FooterFeedbackMixin(FooterMixin):
    def _test_footer(self):
        super(FooterFeedbackMixin, self)._test_footer()
        # check that we have an email
        self.assertValidFeedbackLink(self.footer_selector + " a[class=feedback-email]")

        # check that we have the support email
        selector = self.footer_selector + " a[class=support-email]"
        self.assertHrefEqual(selector, SUPPORT_EMAIL)


class PrimaryNavMixin(CourseApiMixin):
    # set to True if the URL fragement should be checked when testing the skip link
    test_skip_link_url = True

    def _test_user_menu(self):
        """
        Verify the user menu functions properly.
        """
        element = self.page.q(css='.active-user.dropdown-toggle')
        self.assertTrue(element.present)
        self.assertEqual(element.attrs('aria-expanded')[0], 'false')

        element.click()

        # Ensure the menu is actually visible onscreen
        element = self.page.q(css='ul.dropdown-menu.active-user-nav')
        self.assertTrue(element.visible)

    def _test_active_course(self):
        """ Ensure the active course item contains either the course name or ID. """
        course_id = getattr(self.page, 'course_id', None)

        if not course_id:
            return skip('Page has no course_id attribute set.')

        element = self.page.q(css='.navbar-header .active-course-name')
        self.assertTrue(element.visible)

        course_name = self.get_course_name_or_id(course_id)
        self.assertEqual(element.text[0], course_name)

    def _test_skip_link(self, test_url):
        active_element = self.driver.switch_to.active_element
        skip_link = self.page.q(css='.skip-link').results[0]
        skip_link_ref = '#' + skip_link.get_attribute('href').split('#')[-1]
        target_element = self.page.q(css=skip_link_ref)
        self.assertEqual(len(target_element), 1)

        active_element.send_keys(Keys.TAB)
        active_element = self.driver.switch_to.active_element
        active_element.send_keys(Keys.ENTER)

        if test_url:
            url_hash = self.driver.execute_script('return window.location.hash;')
            self.assertEqual(url_hash, skip_link_ref)

    def test_page(self):
        self._test_skip_link(self.test_skip_link_url)
        self._test_user_menu()
        self._test_active_course()


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


class LogoutMixin(object):
    def logout(self):
        url = '{}/accounts/logout/'.format(DASHBOARD_SERVER_URL)
        self.browser.get(url)


class ContextSensitiveHelpMixin(object):
    help_path = 'index.html'

    @property
    def help_url(self):
        return '{0}/{1}'.format(DOC_BASE_URL, self.help_path)

    def test_page(self):
        # Validate the help link
        self.assertHrefEqual('#help', self.help_url)


class SoapboxMessagesMixin(object):
    soapbox_selector = "div[class=announcement-container]"

    def _test_soapbox_messages(self):
        # make sure we have the correct soapbox messages displayed
        element = self.page.q(css=self.soapbox_selector)
        self.assertTrue(element.present)
        self.assertTrue(SOAPBOX_GLOBAL_MESSAGE in element.text)
        self.assertFalse(SOAPBOX_INACTIVE_MESSAGE in element.text)

        if self.page.path == SOAPBOX_SINGLE_PAGE_PATH:
            element = self.page.q(css=self.soapbox_selector)
            self.assertTrue(SOAPBOX_SINGLE_PAGE_MESSAGE in element.text)

    def test_page(self):
        super(SoapboxMessagesMixin, self).test_page()
        self._test_soapbox_messages()


class AnalyticsDashboardWebAppTestMixin(FooterMixin, PrimaryNavMixin, ContextSensitiveHelpMixin, AssertMixin,
                                        LoginMixin, SoapboxMessagesMixin):
    def test_page(self):
        self.login()
        self.page.visit()
        PrimaryNavMixin.test_page(self)
        ContextSensitiveHelpMixin.test_page(self)

    def date_strip_leading_zeroes(self, s):
        """
        Remove the leading 0 on formatted date strings.
        :param s: Date formatted as string
        """
        return s.replace(' 0', ' ')

    @staticmethod
    def format_number(value):
        """ Format the given value for the current locale (e.g. include decimal separator). """
        if isinstance(value, int):
            return locale.format("%d", value, grouping=True)
        return locale.format("%.1f", value, grouping=True)

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

        tooltip_element = self.page.q(css=help_selector + " > span[data-toggle='tooltip']")
        self.assertTrue(tooltip_element.present)
        # the context of title gets move to "data-original-title"
        self.assertEqual(tooltip_element[0].get_attribute('data-original-title'), tip_text)

    def assertMetricTileValid(self, stat_type, value, tooltip):
        selector = 'data-stat-type=%s' % stat_type
        if value is not None:
            self.assertSummaryPointValueEquals(selector, self.format_number(value))
        self.assertSummaryTooltipEquals(selector, tooltip)


class CoursePageTestsMixin(AnalyticsApiClientMixin, FooterLegalMixin, FooterFeedbackMixin,
                           AnalyticsDashboardWebAppTestMixin):
    """ Mixin for common course page assertions and tests. """

    DASHBOARD_DATE_FORMAT = '%B %d, %Y'
    page = None

    def setUp(self):
        super(CoursePageTestsMixin, self).setUp()
        self.api_date_format = self.analytics_api_client.DATE_FORMAT
        self.api_datetime_format = self.analytics_api_client.DATETIME_FORMAT

    def assertDataUpdateMessageEquals(self, value):
        element = self.page.q(css='div.data-update-message')
        self.assertEqual(element.text[0], value)

    def format_time_as_dashboard(self, value):
        return value.strftime(self.DASHBOARD_DATE_FORMAT)

    def _format_last_updated_time(self, d):
        return d.strftime('%I:%M %p').lstrip('0')

    def format_last_updated_date_and_time(self, d):
        return {'update_date': d.strftime(self.DASHBOARD_DATE_FORMAT), 'update_time': self._format_last_updated_time(d)}

    def build_display_percentage(self, count, total, zero_percent_default='0.0%'):
        if total and count:
            percent = count / float(total) * 100.0
            return '{:.1f}%'.format(percent) if percent >= 1.0 else '< 1%'
        return zero_percent_default

    def _get_data_update_message(self):
        raise NotImplementedError

    def _test_data_update_message(self):
        """ Validate the content in the data update message container. """

        message = self._get_data_update_message()
        self.assertDataUpdateMessageEquals(message)

    def _test_course_home_nav(self):
        element = self.page.q(css='.course-label')
        self.assertEqual(element.text[0], 'Course Home')

    def test_page(self):
        """
        Primary test method.

        Sub-classes should override this method and add additional tests. Sub-classes can safely assume that, if tests
        pass, execution of this parent method will leave the browser on the page being tested.
        :return:
        """
        super(CoursePageTestsMixin, self).test_page()
        self._test_data_update_message()
        self._test_course_home_nav()


class CourseDemographicsPageTestsMixin(CoursePageTestsMixin):
    demographic_type = None
    data_information_message = 'All above demographic data was self-reported at the time of registration.'
    chart_selector = '#enrollment-chart-view'
    table_section_selector = 'div[data-role=enrollment-table]'
    table_download_selector = 'a[data-role=enrollment-csv]'
    table_columns = None
    demographic_data = None

    def test_page(self):
        super(CourseDemographicsPageTestsMixin, self).test_page()
        self._test_data_information_message()
        self._test_chart()
        self._test_table()

    def _test_chart(self):
        self.fulfill_loading_promise(self.chart_selector)
        self.assertElementHasContent(self.chart_selector)

    # pylint: disable=unsubscriptable-object
    def _test_table(self):
        self.assertTable(self.table_section_selector, self.table_columns, self.table_download_selector)

        rows = self.page.browser.find_elements_by_css_selector('{} tbody tr'.format(self.table_section_selector))
        self.assertGreater(len(rows), 0)
        sum_count = 0.0
        if self.demographic_data and 'count' in self.demographic_data[0]:
            sum_count = float(sum([datum['count'] for datum in self.demographic_data]))

        for i, row in enumerate(rows):
            columns = row.find_elements_by_css_selector('td')
            self._test_table_row(self.demographic_data[i], columns, sum_count)

    def _test_table_row(self, datum, column, sum_count):
        raise NotImplementedError

    def _test_data_information_message(self):
        element = self.page.q(css='div.data-information-message')
        self.assertEqual(element.text[0], self.data_information_message)

    def _get_data_update_message(self):
        return self._build_data_update_message(self.course.enrollment(self.demographic_type))

    def _build_data_update_message(self, api_response):
        current_data = api_response[0]
        last_updated = datetime.datetime.strptime(current_data['created'], self.api_datetime_format)
        return 'Demographic learner data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)
