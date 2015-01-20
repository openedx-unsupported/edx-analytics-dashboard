import datetime

from bok_choy.web_app_test import WebAppTest

from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CoursePerformanceAnswerDistributionPage


_multiprocess_can_split_ = True


class CoursePerformanceAnswerDistributionTests(CoursePageTestsMixin, WebAppTest):

    help_path = 'performance/index.html'

    def setUp(self):
        super(CoursePerformanceAnswerDistributionTests, self).setUp()
        self.page = CoursePerformanceAnswerDistributionPage(self.browser)
        self.module = self.analytics_api_client.modules(self.page.course_id, self.page.problem_id)
        api_response = self.module.answer_distribution()
        data = [i for i in api_response if i['part_id'] == self.page.part_id]
        self.answer_distribution = sorted(data, key=lambda a: a['count'], reverse=True)


    def _get_data_update_message(self):
        current_data = self.answer_distribution[0]
        last_updated = datetime.datetime.strptime(current_data['created'], self.api_datetime_format)
        return 'Answer distribution data was last updated %(update_date)s at %(update_time)s UTC.' % \
               self.format_last_updated_date_and_time(last_updated)

    def test_page(self):
        super(CoursePerformanceAnswerDistributionTests, self).test_page()
        self._test_heading_question()
        self._test_problem_description()
        self._test_chart()
        self._test_table()

    def _test_heading_question(self):
        element = self.page.q(css='.section-heading')
        self.assertEqual(element.text[0], 'How did students answer this part of the problem?')

    def _test_problem_description(self):
        section_selector = '.problem-description'

        element = self.page.q(css=section_selector + ' p')
        self.assertIsNotNone(element[0])

        self.assertValidHref(section_selector + ' a')

    def _test_chart(self):
        chart_selector = '#performance-chart-view'
        self.fulfill_loading_promise(chart_selector)
        self.assertElementHasContent(chart_selector)

        element = self.page.q(css='#distQuestionsMenu')
        self.assertIn('Submissions for Part', element[0].text)

        container_selector = '.analytics-chart-container'
        element = self.page.q(css=container_selector + ' i')
        expected_tooltip = 'This graph includes every answer submitted by a student for this problem, and shows ' \
                           'the number of students who submitted each answer.  A maximum of 12 answers are shown.'
        self.assertEqual(element[0].get_attribute('data-original-title'), expected_tooltip)

    def _test_table(self):
        table_section_selector = "div[data-role=performance-table]"
        self.assertTable(table_section_selector, ['Answer', 'Correct', 'Submission Count'],
                         'a[data-role=performance-csv]')

        rows = self.page.browser.find_elements_by_css_selector('{} tbody tr'.format(table_section_selector))

        value_field = 'answer_value_text'
        if self.answer_distribution[0]['answer_value_text'] is None:
            value_field = 'answer_value_numeric'

        for i, row in enumerate(rows):
            answer = self.answer_distribution[i]
            columns = row.find_elements_by_css_selector('td')

            actual = []
            for col in columns:
                actual.append(col.text)

            answer_value = answer[value_field]
            if value_field == 'answer_value_numeric':
                answer_value = str(('%f' % answer_value).rstrip('0').rstrip('.'))
            expected = [answer_value]
            correct = '-'
            if answer['correct']:
                correct = 'Correct'
            expected.append(correct)
            expected.append(str(answer['count']))

            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[2].get_attribute('class'))
