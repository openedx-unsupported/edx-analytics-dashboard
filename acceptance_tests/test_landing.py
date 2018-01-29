from bok_choy.web_app_test import WebAppTest

from acceptance_tests import OPEN_SOURCE_URL, RESEARCH_URL, SUPPORT_EMAIL, SHOW_LANDING_RESEARCH
from acceptance_tests.mixins import LoginMixin, LogoutMixin, FooterLegalMixin, PageTestMixin
from acceptance_tests.pages import LandingPage


_multiprocess_can_split_ = False


class LandingTests(PageTestMixin, LoginMixin, LogoutMixin, FooterLegalMixin, WebAppTest):
    def setUp(self):
        super(LandingTests, self).setUp()
        self.page = LandingPage(self.browser)

    def test_page(self):
        super(LandingTests, self).test_page()
        # landing page will not be viewable by logged in users
        self.page.browser.get(self.page.path)
        self.assertFalse(self.page.is_browser_on_page())

        # landing page only accessible to logged out users
        self.logout()
        # logout page will redirect to the landing page
        self._test_lenses()
        self._test_audience_messages()

    def _test_lenses(self):
        question_elements = self.page.q(css='.lens-question')
        self.assertTrue(question_elements.present)

        expected_questions = ['Who are my learners?', 'What are learners engaging with in my course?',
                              'How well is my content supporting learners?']
        num_lenses = len(expected_questions)
        self.assertEqual(len(question_elements), num_lenses)

        for i in range(num_lenses):
            self.assertEqual(question_elements[i].text, expected_questions[i])

        summary_elements = self.page.q(css='.lens-summary')
        self.assertTrue(summary_elements.present)
        self.assertTrue(len(summary_elements), num_lenses)

        lens_icon_elements = self.page.q(css='.lens-summary h1 span')
        self.assertTrue(lens_icon_elements.present)
        self.assertTrue(len(lens_icon_elements), num_lenses)

        # make sure that the icons are hidden from screen readers
        for i in range(num_lenses):
            self.assertEqual(lens_icon_elements.attrs('aria-hidden')[i], 'true')

    def _test_audience_messages(self):
        element = self.page.q(css='.audience-message')
        self.assertTrue(element.present)

        expected_headers = ['Join the Open Source Community', 'Need Help?']
        if SHOW_LANDING_RESEARCH:
            expected_headers.insert(1, 'Research at edX')
        num_actions = len(expected_headers)

        module_selector = '.audience-message-module'
        header_elements = self.page.q(css=module_selector + ' h1')
        self.assertTrue(header_elements.present)
        self.assertEqual(len(header_elements), num_actions)

        action_link_elements = self.page.q(css=module_selector + ' a')
        self.assertTrue(action_link_elements.present)
        self.assertEqual(len(action_link_elements), num_actions)

        expected_links = [OPEN_SOURCE_URL, RESEARCH_URL, 'mailto:{}'.format(SUPPORT_EMAIL)]
        for i in range(num_actions):
            self.assertEqual(header_elements[i].text, expected_headers[i])
            self.assertEqual(action_link_elements.attrs('href')[i], expected_links[i])
