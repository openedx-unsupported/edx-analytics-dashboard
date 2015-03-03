from collections import namedtuple
import datetime
import logging

from analyticsclient.exceptions import NotFoundError
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import slumber

import common
from courses import utils
from courses.exceptions import NoAnswerSubmissionsError
from courses.presenters import BasePresenter
from core.utils import sanitize_cache_key


logger = logging.getLogger(__name__)

# Stores the answer distribution return from CoursePerformancePresenter
AnswerDistributionEntry = namedtuple('AnswerDistributionEntry', [
    'last_updated',
    'questions',
    'active_question',
    'answer_distribution',
    'answer_distribution_limited',
    'is_random',
    'answer_type',
    'problem_part_description'
])


class CoursePerformancePresenter(BasePresenter):
    """
    Presenter for the performance page.
    """
    _last_updated = None

    # limit for the number of bars to display in the answer distribution chart
    CHART_LIMIT = 12

    # minimum screen space a grading policy bar will take up (even if a policy is 0%, display some bar)
    MIN_POLICY_DISPLAY_PERCENT = 5

    def __init__(self, access_token, course_id, timeout=10):
        super(CoursePerformancePresenter, self).__init__(course_id, timeout)
        self.course_api_client = slumber.API(settings.COURSE_API_URL,
                                             auth=common.BearerAuth(access_token))

    def get_answer_distribution(self, problem_id, problem_part_id):
        """
        Retrieve answer distributions for a particular module/problem and problem part.
        """

        module = self.client.modules(self.course_id, problem_id)

        api_response = module.answer_distribution()
        questions = self._build_questions(api_response)

        filtered_active_question = [i for i in questions if i['part_id'] == problem_part_id]
        if len(filtered_active_question) == 0:
            raise NotFoundError
        else:
            active_question = filtered_active_question[0]['question']

        answer_distributions = self._build_answer_distribution(api_response, problem_part_id)
        problem_part_description = self._build_problem_description(problem_part_id, questions)

        is_random = self._is_answer_distribution_random(answer_distributions)
        answer_distribution_limited = None
        if not is_random:
            # only display the top in the chart
            answer_distribution_limited = answer_distributions[:self.CHART_LIMIT]

        answer_type = self._get_answer_type(answer_distributions)
        last_updated = self.parse_api_datetime(answer_distributions[0]['created'])
        self._last_updated = last_updated

        return AnswerDistributionEntry(last_updated, questions, active_question, answer_distributions,
                                       answer_distribution_limited, is_random, answer_type, problem_part_description)

    def _build_problem_description(self, problem_part_id, questions):
        """ Returns the displayable problem name. """
        problem = [q for q in questions if q['part_id'] == problem_part_id][0]
        return problem['short_description']

    def _get_answer_type(self, answer_distributions):
        """
        Returns either 'text' or 'numeric' to describe the answer and used in the JS table to format
        and sort the dataset.
        """
        field = 'answer_value'
        for ad in answer_distributions:
            if ad[field] is not None and not utils.number.is_number(ad[field]):
                return 'text'
        return 'numeric'

    def _is_answer_distribution_random(self, answer_distributions):
        """
        Problems are considered randomized if variant is populated with values
        greater than 1.
        """
        for ad in answer_distributions:
            variant = ad['variant']
            if variant is not None and variant is not 1:
                return True
        return False

    def _build_questions(self, answer_distributions):
        """
        Builds the questions and part_id from the answer distribution. Displayed
        drop down.
        """
        questions = []
        part_id_to_problem = {}

        # Collect unique questions from the answer distribution
        for question_answer in answer_distributions:
            question = question_answer.get('question_text', None)
            problem_name = question_answer.get('problem_display_name', None)
            part_id_to_problem[question_answer['part_id']] = {
                'question': question,
                'problem_name': problem_name
            }

        for part_id, problem in part_id_to_problem.iteritems():
            questions.append({
                'part_id': part_id,
                'question': problem['question'],
                'problem_name': problem['problem_name']
            })

        utils.sorting.natural_sort(questions, 'part_id')

        # add an enumerated label
        has_parts = len(questions) > 1
        for i, question in enumerate(questions):
            text = question['question']
            question_num = i + 1
            question_template = _('Submissions')
            short_description_template = ''
            if text:
                if has_parts:
                    question_template = _('Submissions for Part {part_number}: {part_description}')
                    short_description_template = _('Part {part_number}: {part_description}')
                else:
                    question_template = _('Submissions: {part_description}')
                    short_description_template = _('{part_description}')
            else:
                if has_parts:
                    question_template = _('Submissions for Part {part_number}')
                    short_description_template = _('Part {part_number}')

            # pylint: disable=no-member
            question['question'] = question_template.format(part_number=question_num, part_description=text)
            question['short_description'] = short_description_template.format(
                part_number=question_num, part_description=text)

        return questions

    def _build_answer_distribution(self, api_response, problem_part_id):
        """ Filter for this problem part and sort descending order. """
        answer_distributions = [i for i in api_response if i['part_id'] == problem_part_id]
        answer_distributions = sorted(answer_distributions, key=lambda a: -a['count'])
        return answer_distributions

    def get_cache_key(self, name):
        return sanitize_cache_key('{}_{}'.format(self.course_id, name))

    @property
    def last_updated(self):
        if not self._last_updated:
            key = self.get_cache_key('problems_last_updated')
            self._last_updated = cache.get(key)

        return self._last_updated

    def grading_policy(self):
        """ Returns the grading policy for the represented course."""
        key = self.get_cache_key('grading_policy')
        grading_policy = cache.get(key)

        if not grading_policy:
            logger.debug('Retrieving grading policy for course: %s', self.course_id)
            grading_policy = self.course_api_client.grading_policies(self.course_id).get()
            cache.set(key, grading_policy)

        return grading_policy

    def get_max_policy_display_percent(self, grading_policy):
        """
        Returns the maximum width that a grading bar can be for display, given
        the min width, MIN_POLICY_DISPLAY_PERCENT.
        """
        max_percent = 100
        for policy in grading_policy:
            if policy['weight'] < (self.MIN_POLICY_DISPLAY_PERCENT / 100.0):
                max_percent -= self.MIN_POLICY_DISPLAY_PERCENT
        return max_percent

    def assignment_types(self):
        """ Returns the assignment types for the represented course."""
        grading_policy = self.grading_policy()
        return [gp['assignment_type'] for gp in grading_policy]

    def _course_problems(self):
        """ Retrieves course problems (from cache or course API) and adds submission data. """

        key = self.get_cache_key('problems')
        problems = cache.get(key)

        if not problems:
            # Get the problems from the API
            logger.debug('Retrieving problem submissions for course: %s', self.course_id)

            try:
                problems = self.client.courses(self.course_id).problems()
            except NotFoundError:
                raise NoAnswerSubmissionsError(course_id=self.course_id)

            # Create a lookup table so that submission data can be quickly retrieved by downstream consumers.
            table = {}
            last_updated = datetime.datetime.min

            for problem in problems:
                # Change the id key name
                problem['id'] = problem.pop('module_id')

                # Add an percent and incorrect_submissions field
                total = problem['total_submissions']
                problem['correct_percent'] = utils.math.calculate_percent(problem['correct_submissions'], total)
                problem['incorrect_submissions'] = total - problem['correct_submissions']
                problem['incorrect_percent'] = utils.math.calculate_percent(problem['incorrect_submissions'], total)

                table[problem['id']] = problem

                # Set the last_updated value
                created = problem.pop('created', None)
                if created:
                    created = self.parse_api_datetime(created)
                    last_updated = max(last_updated, created)

            if last_updated is not datetime.datetime.min:
                _key = self.get_cache_key('problems_last_updated')
                cache.set(_key, last_updated)
                self._last_updated = last_updated

            problems = table
            cache.set(key, problems)

        return problems

    def _add_submissions_and_part_ids(self, assignments):
        """ Adds submissions and part IDs to the given assignments. """

        DEFAULT_DATA = {
            'total_submissions': 0,
            'correct_submissions': 0,
            'correct_percent': 0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0,
            'part_ids': []
        }

        try:
            course_problems = self._course_problems()
        except NoAnswerSubmissionsError as e:
            logger.warning(e)
            course_problems = {}

        for assignment in assignments:
            problems = assignment['problems']

            for index, problem in enumerate(problems):
                data = course_problems.get(problem['id'], DEFAULT_DATA)

                # map empty names to None so that the UI catches them and displays as '(empty)'
                if len(problem['name']) < 1:
                    problem['name'] = None
                data['index'] = index + 1

                # not all problems have submissions
                if len(data['part_ids']) > 0:
                    utils.sorting.natural_sort(data['part_ids'])
                    data['url'] = reverse('courses:performance:answer_distribution',
                                          kwargs={
                                              'course_id': self.course_id,
                                              'assignment_id': assignment['id'],
                                              'problem_id': problem['id'],
                                              'problem_part_id': data['part_ids'][0]
                                          })
                problem.update(data)

            assignment['problems'] = problems

    def _structure(self):
        """ Retrieves course structure from the course API. """
        key = self.get_cache_key('structure')
        structure = cache.get(key)

        if not structure:
            logger.debug('Retrieving structure for course: %s', self.course_id)
            structure = self.course_api_client.course_structures(self.course_id).get()
            cache.set(key, structure)

        return structure

    def assignments(self, assignment_type=None):
        """ Returns the assignments (and problems) for the represented course. """

        assignment_type_key = self.get_cache_key('assignments_{}'.format(assignment_type))
        assignments = cache.get(assignment_type_key)

        if not assignments:
            all_assignments_key = '{}_assignments'.format(self.course_id)
            assignments = cache.get(all_assignments_key)

            if not assignments:
                structure = self._structure()
                assignments = common.CourseStructure.course_structure_to_assignments(
                    structure, graded=True, assignment_type=None)
                cache.set(all_assignments_key, assignments)

            if assignment_type:
                assignment_type = assignment_type.lower()
                assignments = [assignment for assignment in assignments if
                               assignment['assignment_type'].lower() == assignment_type]

            self._add_submissions_and_part_ids(assignments)

            for index, assignment in enumerate(assignments):
                problems = assignment['problems']
                total_submissions = sum(problem.get('total_submissions', 0) for problem in problems)
                correct_submissions = sum(problem.get('correct_submissions', 0) for problem in problems)
                assignment['num_problems'] = len(problems)
                assignment['total_submissions'] = total_submissions
                assignment['correct_submissions'] = correct_submissions
                assignment['correct_percent'] = utils.math.calculate_percent(correct_submissions, total_submissions)
                assignment['incorrect_submissions'] = total_submissions - correct_submissions
                assignment['incorrect_percent'] = utils.math.calculate_percent(
                    assignment['incorrect_submissions'], total_submissions)
                assignment['index'] = index + 1
                # removing the URL keeps navigation between the menu and bar chart consistent
                if assignment['total_submissions'] > 0:
                    assignment['url'] = reverse('courses:performance:assignment',
                                                kwargs={'course_id': self.course_id, 'assignment_id': assignment['id']})

            # Cache the data for the course-assignment_type combination.
            cache.set(assignment_type_key, assignments)

        return assignments

    def has_submissions(self, assignments):
        for assignment in assignments:
            if assignment['total_submissions'] > 0:
                return True
        return False

    def assignment(self, assignment_id):
        """ Retrieve a specific assignment. """
        filtered = [assignment for assignment in self.assignments() if assignment['id'] == assignment_id]
        if filtered:
            return filtered[0]
        else:
            return None

    def problem(self, problem_id):
        """ Retrieve a specific problem. """
        problem = self._structure()['blocks'][problem_id]
        problem['name'] = problem.pop('display_name')
        return problem
