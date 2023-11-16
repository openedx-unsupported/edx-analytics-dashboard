from acceptance_tests import (
    COURSE_API_KEY,
    COURSE_API_URL,
    DASHBOARD_FEEDBACK_EMAIL,
    DOC_BASE_URL,
    ENABLE_COURSE_API,
)
from common.clients import CourseStructureApiClient


class CourseApiMixin:
    course_api_client = None

    def setUp(self):
        super().setUp()

        if ENABLE_COURSE_API:
            self.course_api_client = CourseStructureApiClient(COURSE_API_URL, COURSE_API_KEY, 5)

    def get_course_name_or_id(self, course_id):
        """ Returns the course name if the course API is enabled; otherwise, the course ID. """
        course_name = course_id
        if ENABLE_COURSE_API:
            course_name = self.course_api_client.courses(course_id).get()['name']

        return course_name


class AssertMixin:
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
        rows = self.page.q(css='%s thead th' % table_selector)
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

        rows = self.page.browser.find_elements_by_css_selector(f'{table_selector} tbody tr')
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


class ContextSensitiveHelpMixin:
    help_path = 'index.html'

    @property
    def help_url(self):
        return f'{DOC_BASE_URL}/{self.help_path}'

    def test_page(self):
        # Validate the help link
        self.assertHrefEqual('#help', self.help_url)
