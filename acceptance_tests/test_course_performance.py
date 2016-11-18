import datetime
from unittest import skipUnless

from bok_choy.web_app_test import WebAppTest

from acceptance_tests import ENABLE_COURSE_API
from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CoursePerformanceUngradedContentPage, \
    CoursePerformanceGradedContentPage, CoursePerformanceAnswerDistributionPage, \
    CoursePerformanceGradedContentByTypePage, CoursePerformanceAssignmentPage, \
    CoursePerformanceUngradedSectionPage, CoursePerformanceUngradedSubsectionPage, \
    CoursePerformanceUngradedAnswerDistributionPage
from common.course_structure import CourseStructure


_multiprocess_can_split_ = True


class CoursePerformancePageTestsMixin(CoursePageTestsMixin):

    help_path = 'performance/Performance_Answers.html'
    table_selector = 'div[data-role="data-table"]'

    def test_page(self):
        super(CoursePerformancePageTestsMixin, self).test_page()
        self._test_chart()
        self._test_table()

    def _test_chart(self):
        chart_selector = '#chart-view'
        self.fulfill_loading_promise(chart_selector)
        self.assertElementHasContent(chart_selector)

    def _test_table(self):
        raise NotImplementedError

    def _get_data_update_message(self):
        problems = self.course.problems()
        last_updated = datetime.datetime.min

        for problem in problems:
            last_updated = max(last_updated, datetime.datetime.strptime(problem['created'], self.api_datetime_format))

        updated_date_and_time = self.format_last_updated_date_and_time(last_updated)
        return ('Problem submission data was last updated {} at {} UTC.').format(
            updated_date_and_time['update_date'], updated_date_and_time['update_time'])

    def _format_number_or_hyphen(self, value):
        if value:
            return self.format_number(value)
        else:
            return '-'

    def _build_display_percentage_or_hyphen(self, correct, total):
        if correct:
            return self.build_display_percentage(correct, total)
        else:
            return '-'

    def _get_problems_dict(self):
        # Retrieve the submissions from the Analytics Data API and create a lookup table.
        problems = self.course.problems()
        return {problem['module_id']: problem for problem in problems}

    def _get_assignments(self, assignment_type=None):
        blocks = self.course_api_client.blocks().get()
        assignments = CourseStructure.course_structure_to_assignments(blocks, graded=True,
                                                                      assignment_type=assignment_type)

        return self._build_submissions(assignments, self._get_problems_dict())

    def _get_sections(self):
        blocks = self.course_api_client.blocks().get()
        sections = CourseStructure.course_structure_to_sections(blocks, 'problem', graded=False)
        problems = self._get_problems_dict()
        for section in sections:
            self._build_submissions(section['children'], problems)
        return self._build_submissions(sections, problems)

    def _find_child_block(self, blocks, child_id):
        for block in blocks:
            if block[u'id'] == child_id:
                return block
        return None

    def _build_submissions(self, blocks, problems):
        # Sum the submission counts
        for parent_block in blocks:
            total = 0
            correct = 0
            num_modules = 0

            for child_block in parent_block['children']:
                submission_entry = problems.get(child_block['id'], None)

                if submission_entry:
                    total += submission_entry['total_submissions']
                    correct += submission_entry['correct_submissions']
                    num_modules += 1

                    child_block.update({
                        'total_submissions': submission_entry['total_submissions'],
                        'correct_submissions': submission_entry['correct_submissions'],
                        'num_modules': 1
                    })
                elif 'total_submissions' in child_block and 'correct_submissions' in child_block:
                    total += child_block['total_submissions']
                    correct += child_block['correct_submissions']
                    num_modules += child_block['num_modules']
                else:
                    num_modules += 1
                    child_block.update({
                        'total_submissions': 0,
                        'correct_submissions': 0,
                        'num_modules': 1,
                    })

            parent_block.update({
                'total_submissions': total,
                'correct_submissions': correct,
                'num_modules': num_modules
            })

        return blocks

    def assertBlockRows(self, blocks):
        table = self.page.browser.find_element_by_css_selector(self.table_selector)
        rows = table.find_elements_by_css_selector('tbody tr')
        self.assertEqual(len(rows), len(blocks))

        for index, row in enumerate(rows):
            block = blocks[index]
            cols = row.find_elements_by_css_selector('td')
            self.assertRowTextEquals(cols, self.get_expected_row(index, block))

    def get_expected_row(self, index, block):
        return [unicode(index + 1), block['name']]


# pylint: disable=abstract-method
class CoursePerformanceAveragedTableMixin(CoursePerformancePageTestsMixin):

    def get_expected_row(self, index, block):
        row = super(CoursePerformanceAveragedTableMixin, self).get_expected_row(index, block)
        num_modules_denominator = float(block.get('num_modules', 1))
        row += [
            unicode(self._format_number_or_hyphen(block.get('num_modules', 0))),
            unicode(self._format_number_or_hyphen(block['correct_submissions'] / num_modules_denominator
                                                  if num_modules_denominator else None)),
            unicode(self._format_number_or_hyphen(
                (block['total_submissions'] - block['correct_submissions']) / num_modules_denominator
                if num_modules_denominator else None)),
            unicode(self._format_number_or_hyphen(block['total_submissions'] / num_modules_denominator
                                                  if num_modules_denominator else None)),
            unicode(self._build_display_percentage_or_hyphen(block['correct_submissions'],
                                                             block['total_submissions']))
        ]
        return row


# pylint: disable=abstract-method
class CoursePerformanceModuleTableMixin(CoursePerformancePageTestsMixin):

    def get_expected_row(self, index, block):
        row = super(CoursePerformanceModuleTableMixin, self).get_expected_row(index, block)
        row += [
            unicode(self._format_number_or_hyphen(block['correct_submissions'])),
            unicode(self._format_number_or_hyphen(
                block['total_submissions'] - block['correct_submissions'])),
            unicode(self._format_number_or_hyphen(block['total_submissions'])),
            unicode(self._build_display_percentage_or_hyphen(block['correct_submissions'],
                                                             block['total_submissions']))
        ]
        return row


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the graded content page.')
class CoursePerformanceGradedContentTests(CoursePerformancePageTestsMixin, WebAppTest):
    """
    Tests for the course graded content page.
    """

    def _test_data_update_message(self):
        # There is no data update message displayed on this page.
        pass

    def _get_grading_policy(self):
        """
        Retrieve the course's grading policy from the Course API.
        """
        policy = self.course_api_client.grading_policies(self.page.course_id).get()

        for item in policy:
            weight = item['weight']
            item['weight_as_percentage'] = u'{:.0f}%'.format(weight * 100)

        return policy

    def setUp(self):
        super(CoursePerformanceGradedContentTests, self).setUp()
        self.page = CoursePerformanceGradedContentPage(self.browser)
        self.grading_policy = self._get_grading_policy()

    def _test_chart(self):
        """
        Test the assignment types display and values.
        """
        elements = self.page.browser.find_elements_by_css_selector('.grading-policy .policy-item')

        for index, element in enumerate(elements):
            grading_policy = self.grading_policy[index]
            assignment_type = grading_policy['assignment_type']

            # Verify the URL to view the assignments is correct.
            actual = element.find_element_by_css_selector('a').get_attribute('href')
            expected = u'{}{}/'.format(self.page.page_url, assignment_type)
            self.assertEqual(actual, expected)

            # Verify the displayed weight
            actual = element.find_element_by_css_selector('.weight').text
            expected = grading_policy['weight_as_percentage']
            self.assertEqual(actual, expected)

            # Verify the weighted column sizes
            style = element.get_attribute('style')
            width = 'width: {}'.format(grading_policy['weight_as_percentage'])
            self.assertIn(width, style)

            # Verify the printed assignment type
            actual = element.find_element_by_css_selector('.type').text
            self.assertEqual(actual, assignment_type)

    def _test_table(self):
        pass


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the course assignment type detail page.')
class CoursePerformanceGradedContentByTypeTests(CoursePerformanceAveragedTableMixin, WebAppTest):
    """
    Tests for the course assignment type detail page.
    """

    def setUp(self):
        super(CoursePerformanceGradedContentByTypeTests, self).setUp()
        self.page = CoursePerformanceGradedContentByTypePage(self.browser)
        self.assignment_type = self.page.assignment_type
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.assignments = self._get_assignments(self.assignment_type)

    def _test_table(self):
        self.assertTableColumnHeadingsEqual(self.table_selector,
                                            [u'Order', u'Assignment Name', u'Problems',
                                             u'Average Correct', u'Average Incorrect',
                                             u'Average Submissions Per Problem', u'Percentage Correct'])
        self.assertBlockRows(self.assignments)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the course assignment detail page.')
class CoursePerformanceAssignmentTests(CoursePerformanceModuleTableMixin, WebAppTest):
    """
    Tests for the course assignment detail page.
    """

    def _get_assignment(self):
        assignments = self._get_assignments()
        for assignment in assignments:
            if assignment[u'id'] == self.assignment_id:
                return assignment

        raise AttributeError('Assignment not found!')

    def setUp(self):
        super(CoursePerformanceAssignmentTests, self).setUp()
        self.page = CoursePerformanceAssignmentPage(self.browser)
        self.assignment_id = self.page.assignment_id
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.assignment = self._get_assignment()

    def _test_table(self):
        # Check the column headings
        self.assertTableColumnHeadingsEqual(self.table_selector, [
            u'Order', u'Problem Name', u'Correct', u'Incorrect', u'Total', u'Percentage Correct'])
        self.assertBlockRows(self.assignment['children'])


class CoursePerformanceAnswerDistributionMixin(CoursePerformancePageTestsMixin):

    course = None
    module = None
    answer_distribution = None

    def setUp(self):
        super(CoursePerformanceAnswerDistributionMixin, self).setUp()
        self.page = self.get_page()
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.module = self.analytics_api_client.modules(self.page.course_id, self.page.problem_id)
        api_response = self.module.answer_distribution()
        data = [i for i in api_response if i['part_id'] == self.page.part_id]
        self.answer_distribution = sorted(data, key=lambda a: a['last_response_count'], reverse=True)

    def get_page(self):
        raise NotImplementedError

    def test_page(self):
        super(CoursePerformanceAnswerDistributionMixin, self).test_page()
        self._test_heading_question()
        self._test_problem_description()

    def _test_heading_question(self):
        element = self.page.q(css='.section-heading')
        self.assertEqual(element.text[0], u'How did learners answer this problem?')

    def _test_problem_description(self):
        section_selector = '.module-description'

        element = self.page.q(css=section_selector + ' p')
        self.assertIsNotNone(element[0])

        self.assertValidHref(section_selector + ' a')

    def _test_chart(self):
        chart_selector = '#performance-chart-view'
        self.fulfill_loading_promise(chart_selector)
        self.assertElementHasContent(chart_selector)

        element = self.page.q(css='#distQuestionsMenu')
        if element:
            self.assertIn('Submissions for Part', element[0].text)
        else:
            element = self.page.q(css='.chart-info')
            self.assertIn('Submissions', element[0].text)

        container_selector = '.analytics-chart-container'
        element = self.page.q(css=container_selector + ' i')
        expected_tooltip = 'This chart shows the most common answers submitted by learners, ordered by frequency.'
        self.assertEqual(element[0].get_attribute('data-original-title'), expected_tooltip)

    def _test_table(self):
        table_section_selector = "div[data-role=performance-table]"
        self.assertTable(table_section_selector, ['Answer', 'Correct', 'Submission Count'],
                         'a[data-role=performance-csv]')

        rows = self.page.browser.find_elements_by_css_selector('{} tbody tr'.format(table_section_selector))

        value_field = 'answer_value'

        for i, row in enumerate(rows):
            answer = self.answer_distribution[i]
            columns = row.find_elements_by_css_selector('td')

            actual = []
            for col in columns:
                actual.append(col.text)

            expected = [answer[value_field] if answer[value_field] else u'(empty)']
            correct = u'-'
            if answer['correct']:
                correct = u'Correct'
            expected.append(correct)
            expected.append(self.format_number(answer['last_response_count']))

            self.assertListEqual(actual, expected)
            self.assertIn('text-right', columns[2].get_attribute('class'))


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the answer distribution page.')
class CoursePerformanceAnswerDistributionTests(CoursePerformanceAnswerDistributionMixin, WebAppTest):

    def get_page(self):
        return CoursePerformanceAnswerDistributionPage(self.browser)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test the answer distribution page.')
class CoursePerformanceUngradedAnswerDistributionTests(CoursePerformanceAnswerDistributionMixin, WebAppTest):

    def get_page(self):
        return CoursePerformanceUngradedAnswerDistributionPage(self.browser)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test ungraded content.')
class CoursePerformanceUngradedContentTests(CoursePerformanceAveragedTableMixin, WebAppTest):

    def setUp(self):
        super(CoursePerformanceUngradedContentTests, self).setUp()
        self.page = CoursePerformanceUngradedContentPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.sections = self._get_sections()

    def _test_table(self):
        self.assertTableColumnHeadingsEqual(self.table_selector,
                                            [u'Order', u'Section Name', u'Problems', u'Average Correct',
                                             u'Average Incorrect', u'Average Submissions Per Problem',
                                             u'Percentage Correct'])
        self.assertBlockRows(self.sections)


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test ungraded content.')
class CoursePerformanceUngradedSectionTests(CoursePerformanceAveragedTableMixin, WebAppTest):

    def setUp(self):
        super(CoursePerformanceUngradedSectionTests, self).setUp()
        self.page = CoursePerformanceUngradedSectionPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.section = self._find_child_block(self._get_sections(), self.page.section_id)

    def _test_table(self):
        self.assertTableColumnHeadingsEqual(self.table_selector,
                                            [u'Order', u'Subsection Name', u'Problems', u'Average Correct',
                                             u'Average Incorrect', u'Average Submissions Per Problem',
                                             u'Percentage Correct'])
        self.assertBlockRows(self.section['children'])


@skipUnless(ENABLE_COURSE_API, 'Course API must be enabled to test ungraded content.')
class CoursePerformanceUngradedSubsectionTests(CoursePerformanceModuleTableMixin, WebAppTest):

    def setUp(self):
        super(CoursePerformanceUngradedSubsectionTests, self).setUp()
        self.page = CoursePerformanceUngradedSubsectionPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
        subsections = self._find_child_block(self._get_sections(), self.page.section_id)['children']
        self.problems = self._find_child_block(subsections, self.page.subsection_id)['children']

    def _test_table(self):
        self.assertTableColumnHeadingsEqual(self.table_selector, [u'Order', u'Problem Name', u'Correct',
                                                                  u'Incorrect', u'Total', u'Percentage Correct'])
        self.assertBlockRows(self.problems)
