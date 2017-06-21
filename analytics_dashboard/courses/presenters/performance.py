from collections import namedtuple, OrderedDict
import logging
from slugify import slugify

from analyticsclient.exceptions import NotFoundError
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from edx_rest_api_client.exceptions import HttpClientError
from core.utils import (CourseStructureApiClient, sanitize_cache_key)

from common.course_structure import CourseStructure
from courses import utils
from courses.exceptions import (BaseCourseError, NoAnswerSubmissionsError)
from courses.presenters import (CoursePresenter, CourseAPIPresenterMixin)


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


class CoursePerformancePresenter(CourseAPIPresenterMixin, CoursePresenter):
    """
    Presenter for the performance page.
    """

    # limit for the number of bars to display in the answer distribution chart
    CHART_LIMIT = 12

    # minimum screen space a grading policy bar will take up (even if a policy is 0%, display some bar)
    MIN_POLICY_DISPLAY_PERCENT = 5

    def __init__(self, access_token, course_id, timeout=settings.LMS_DEFAULT_TIMEOUT):
        super(CoursePerformancePresenter, self).__init__(access_token, course_id, timeout)
        self.grading_policy_client = CourseStructureApiClient(settings.GRADING_POLICY_API_URL, access_token)

    def course_module_data(self):
        try:
            return self._course_module_data()
        except BaseCourseError:
            raise NotFoundError

    def get_answer_distribution(self, problem_id, problem_part_id):
        """
        Retrieve answer distributions for a particular module/problem and problem part.
        """

        module = self.client.modules(self.course_id, problem_id)

        api_response = module.answer_distribution()
        questions = self._build_questions(api_response)

        filtered_active_question = [i for i in questions if i['part_id'] == problem_part_id]
        if not filtered_active_question:
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

    # pylint: disable=redefined-variable-type
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
        for answer_dist in answer_distributions:
            # First and last response counts were added, we can handle both types of API responses at the moment.
            # If just the count is specified it is assumed to be the last response count.
            # TODO: teach downstream logic about first and last response counts
            count = answer_dist.get('last_response_count')
            if count is not None:
                answer_dist['count'] = count
        answer_distributions = sorted(answer_distributions, key=lambda a: -a['count'])
        return answer_distributions

    def grading_policy(self):
        """ Returns the grading policy for the represented course."""
        key = self.get_cache_key('grading_policy')
        grading_policy = cache.get(key)

        if not grading_policy:
            logger.debug('Retrieving grading policy for course: %s', self.course_id)
            grading_policy = self.grading_policy_client.courses(self.course_id).policy.get()

            # Remove empty assignment types as they are not useful and will cause issues downstream.
            grading_policy = [item for item in grading_policy if item['assignment_type']]

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

        # return the results in a similar format to the course structure for standard parsing
        return [
            {
                'name': gp['assignment_type'],
                'url': reverse('courses:performance:graded_content_by_type',
                               kwargs={
                                   'course_id': self.course_id,
                                   'assignment_type': slugify(gp['assignment_type'])
                               })
            } for gp in grading_policy
        ]

    def fetch_course_module_data(self):
        # Implementation of abstract method.  Returns problems from data api.
        try:
            problems = self.client.courses(self.course_id).problems()
        except NotFoundError:
            raise NoAnswerSubmissionsError(course_id=self.course_id)
        return problems

    def attach_computed_data(self, problem):
        # Change the id key name
        problem['id'] = problem.pop('module_id')
        # Add an percent and incorrect_submissions field
        total = problem['total_submissions']
        problem['correct_percent'] = utils.math.calculate_percent(problem['correct_submissions'], total)
        problem['incorrect_submissions'] = total - problem['correct_submissions']
        problem['incorrect_percent'] = utils.math.calculate_percent(problem['incorrect_submissions'], total)

    def post_process_adding_data_to_blocks(self, data, parent_block, child_block, url_func=None):
        # not all problems have submissions
        if data['part_ids']:
            utils.sorting.natural_sort(data['part_ids'])
            if url_func:
                data['url'] = url_func(parent_block, child_block, data)

    @property
    def default_block_data(self):
        return {
            'total_submissions': 0,
            'correct_submissions': 0,
            'correct_percent': 0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0,
            'part_ids': []
        }

    def assignments(self, assignment_type=None):
        """ Returns the assignments (and problems) for the represented course. """

        assignment_type_name = None if assignment_type is None else assignment_type['name']
        assignment_type_key = self.get_cache_key(u'assignments_{}'.format(assignment_type_name))
        assignments = cache.get(assignment_type_key)

        if not assignments:
            all_assignments_key = self.get_cache_key(u'assignments')
            assignments = cache.get(all_assignments_key)

            if not assignments:
                structure = self._get_structure()
                assignments = CourseStructure.course_structure_to_assignments(
                    structure, graded=True, assignment_type=None)
                cache.set(all_assignments_key, assignments)

            if assignment_type:
                assignment_type['name'] = assignment_type['name'].lower()
                assignments = [assignment for assignment in assignments if
                               assignment['assignment_type'].lower() == assignment_type['name']]

            self.add_child_data_to_parent_blocks(assignments, self._build_graded_answer_distribution_url)
            self.attach_data_to_parents(assignments, self._build_assignment_url)

            # Cache the data for the course-assignment_type combination.
            cache.set(assignment_type_key, assignments)

        return assignments

    def attach_aggregated_data_to_parent(self, index, parent, url_func=None):
        children = parent['children']
        total_submissions = sum(child.get('total_submissions', 0) for child in children)
        correct_submissions = sum(child.get('correct_submissions', 0) for child in children)
        incorrect_submissions = total_submissions - correct_submissions
        parent.update({
            'total_submissions': total_submissions,
            'correct_submissions': correct_submissions,
            'correct_percent': utils.math.calculate_percent(correct_submissions, total_submissions),
            'incorrect_submissions': incorrect_submissions,
            'incorrect_percent': utils.math.calculate_percent(incorrect_submissions, total_submissions),
            'index': index + 1,
            'average_submissions': 0,
            'average_correct_submissions': 0,
            'average_incorrect_submissions': 0,
        })

        if parent['num_modules']:
            num_modules = float(parent['num_modules'])
            parent.update({
                'average_submissions': total_submissions / num_modules,
                'average_correct_submissions': correct_submissions / num_modules,
                'average_incorrect_submissions': incorrect_submissions / num_modules,
            })

        # removing the URL keeps navigation between the menu and bar chart consistent
        if url_func and parent['total_submissions'] > 0:
            parent['url'] = url_func(parent)

    def _build_graded_answer_distribution_url(self, parent, problem, parts):
        return reverse('courses:performance:answer_distribution',
                       kwargs={
                           'course_id': self.course_id,
                           'assignment_id': parent['id'],
                           'problem_id': problem['id'],
                           'problem_part_id': parts['part_ids'][0]
                       })

    def build_module_url_func(self, section_id):
        def build_url(parent, problem, parts):
            return reverse('courses:performance:ungraded_answer_distribution',
                           kwargs={
                               'course_id': self.course_id,
                               'section_id': section_id,
                               'subsection_id': parent['id'],
                               'problem_id': problem['id'],
                               'problem_part_id': parts['part_ids'][0]
                           })

        return build_url

    def _build_assignment_url(self, assignment):
        return reverse('courses:performance:assignment', kwargs={
            'course_id': self.course_id, 'assignment_id': assignment['id']})

    def build_section_url(self, section):
        return reverse('courses:performance:ungraded_section', kwargs={'course_id': self.course_id,
                                                                       'section_id': section['id']})

    def build_subsection_url_func(self, section_id):
        """
        Returns a function for creating the ungraded subsection URL.
        """
        # Using closures to keep the section ID available
        def subsection_url(subsection):
            return reverse('courses:performance:ungraded_subsection',
                           kwargs={'course_id': self.course_id,
                                   'section_id': section_id,
                                   'subsection_id': subsection['id']})
        return subsection_url

    def blocks_have_data(self, assignments):
        if assignments:
            for assignment in assignments:
                if assignment['total_submissions'] > 0:
                    return True
        return False

    def assignment(self, assignment_id):
        """ Retrieve a specific assignment. """
        filtered = [assignment for assignment in self.assignments() if assignment['id'] == assignment_id]
        if filtered:
            return filtered[0]
        return None

    @property
    def section_type_template(self):
        return u'ungraded_sections_{}_{}'

    @property
    def all_sections_key(self):
        return u'ungraded_sections'

    @property
    def module_type(self):
        return 'problem'

    @property
    def module_graded_type(self):
        """
        Get ungraded blocks.

        This is a bit confusing as this presenter is used to show both graded and
        ungraded content.  The ungraded content uses CourseAPIPresenterMixin::course_structure
        which then gets the module grade type for filtering.
        """
        return False


class TagsDistributionPresenter(CourseAPIPresenterMixin, CoursePresenter):
    """
    Presenter for the tags distribution page.
    """

    available_tags = None

    @property
    def section_type_template(self):
        return u'tags_problem_sections_{}_{}'

    @property
    def all_sections_key(self):
        return u'tags_problem_sections'

    @property
    def module_type(self):
        return 'tags_problem'

    @property
    def module_graded_type(self):
        return None

    def get_cache_key(self, name):
        return sanitize_cache_key(u'{}_{}'.format(self.course_id, name))

    def fetch_course_module_data(self):
        try:
            problems_and_tags = self.client.courses(self.course_id).problems_and_tags()
        except NotFoundError as e:
            logger.warning("There is no tags distribution info for %s: %s", self.course_id, e)
            return []
        return problems_and_tags

    @property
    def default_block_data(self):
        return {
            'total_submissions': 0,
            'correct_submissions': 0,
            'incorrect_submissions': 0,
            'tags': {}
        }

    def blocks_have_data(self, blocks):
        pass

    def attach_aggregated_data_to_parent(self, index, parent, url_func=None):
        pass

    def attach_computed_data(self, problem):
        problem['id'] = problem.pop('module_id')
        problem['incorrect_submissions'] = problem['total_submissions'] - problem['correct_submissions']

    def get_available_tags(self):
        """
        This function is used to return dict with all emitted unique tag values.
        The return dict format is:
        {
            'tag_name_1': set('tag_value_11', 'tag_value_12',  ... , 'tag_value_1n'),
            'tag_name_2': set('tag_value_21', 'tag_value_22',  ... , 'tag_value_2n'),
            ...
        }
        """
        if not self.available_tags:
            tags_distribution_data = self._get_course_module_data()
            self.available_tags = {}

            for item in tags_distribution_data.values():
                for tag_key, tag_values in item['tags'].iteritems():
                    if tag_key not in self.available_tags:
                        self.available_tags[tag_key] = set()
                    for tag_value in tag_values:
                        self.available_tags[tag_key].add(tag_value)
        return self.available_tags

    def get_tags_content_nav(self, key, selected=None):
        """
        This function is used to create dropdown list with all available values
        for some particular tag. The first argument is the tag key.
        The second argument is the selected tag value.
        """
        result = []
        selected_item = None
        tags = self.get_available_tags()

        if key in tags:
            for item in tags[key]:
                val = {
                    'id': item,
                    'name': item,
                    'url': reverse('courses:performance:learning_outcomes_section',
                                   kwargs={'course_id': self.course_id,
                                           'tag_value': slugify(item)})}
                if selected == slugify(item):
                    selected_item = val
                result.append(val)
        return result, selected_item

    def _get_course_module_data(self):
        try:
            logger.debug("Retrieving tags distribution for course: %s", self.course_id)
            return self._course_module_data()
        except HttpClientError as e:
            logger.error("Unable to retrieve tags distribution info for %s: %s", self.course_id, e)
            return {}

    def _get_course_structure(self):
        def _update_node(updated_structure, origin_structure, node_id, parent_id=None):
            """
            Helper function to get proper course structure.
            Updates the dict that passed as the first argument (adds the parent to each node)
            """
            updated_structure[node_id] = origin_structure[node_id]
            updated_structure[node_id]['parent'] = parent_id if parent_id else None
            for child_id in origin_structure[node_id].get("children", []):
                _update_node(updated_structure, origin_structure, child_id, origin_structure[node_id]['id'])

        updated_structure = OrderedDict()
        origin_structure = self._get_structure()
        if origin_structure:
            _update_node(updated_structure, origin_structure["blocks"], origin_structure['root'])
        return updated_structure

    def get_tags_distribution(self, key):
        tags_distribution_data = self._get_course_module_data()

        result = OrderedDict()
        index = 0

        for item in tags_distribution_data.values():
            if key in item['tags']:
                tag_values = item['tags'][key]
                for tag_value in tag_values:
                    if tag_value not in result:
                        index += 1
                        result[tag_value] = {
                            'id': tag_value,
                            'index': index,
                            'name': tag_value,
                            'num_modules': 0,
                            'total_submissions': 0,
                            'correct_submissions': 0,
                            'incorrect_submissions': 0
                        }
                    result[tag_value]['num_modules'] += 1
                    result[tag_value]['total_submissions'] += item['total_submissions']
                    result[tag_value]['correct_submissions'] += item['correct_submissions']
                    result[tag_value]['incorrect_submissions'] += item['incorrect_submissions']

        for tag_val, item in result.iteritems():
            item.update({
                'average_submissions': (item['total_submissions'] * 1.0) / item['num_modules'],
                'average_correct_submissions': (item['correct_submissions'] * 1.0) / item['num_modules'],
                'average_incorrect_submissions': (item['incorrect_submissions'] * 1.0) / item['num_modules'],
                'correct_percent': utils.math.calculate_percent(item['correct_submissions'],
                                                                item['total_submissions']),
                'incorrect_percent': utils.math.calculate_percent(item['incorrect_submissions'],
                                                                  item['total_submissions']),
                'url': reverse('courses:performance:learning_outcomes_section',
                               kwargs={'course_id': self.course_id,
                                       'tag_value': slugify(tag_val)})
            })
        return result.values()

    def get_modules_marked_with_tag(self, tag_key, tag_value):
        tags_distribution_data = self._get_course_module_data()
        available_tags = self.get_available_tags()
        intermediate = OrderedDict()

        def _get_tags_info(av_tags, tags):
            """
            Helper function to return information about all tags connected with the current item.
            """
            data = {}
            for av_tag_key in av_tags:
                if av_tag_key in tags and tags[av_tag_key]:
                    data[av_tag_key] = u', '.join(tags[av_tag_key])
                else:
                    data[av_tag_key] = None
            return data

        for item in tags_distribution_data.values():
            if tag_key in item['tags']:
                for item_tag_val in item['tags'][tag_key]:
                    if tag_value == slugify(item_tag_val):
                        val = {
                            'id': item['id'],
                            'name': item['id'],
                            'total_submissions': item['total_submissions'],
                            'correct_submissions': item['correct_submissions'],
                            'incorrect_submissions': item['incorrect_submissions'],
                            'correct_percent': utils.math.calculate_percent(item['correct_submissions'],
                                                                            item['total_submissions']),
                            'incorrect_percent': utils.math.calculate_percent(item['incorrect_submissions'],
                                                                              item['total_submissions']),
                            'url': reverse('courses:performance:learning_outcomes_answers_distribution',
                                           kwargs={'course_id': self.course_id,
                                                   'tag_value': tag_value,
                                                   'problem_id': item['id']})
                        }
                        if available_tags:
                            val.update(_get_tags_info(available_tags, item['tags']))
                        intermediate[item['id']] = val

        result = []
        index = 0

        course_structure = self._get_course_structure()

        for key, val in course_structure.iteritems():
            if key in intermediate:
                first_parent = course_structure[val['parent']]
                second_parent = course_structure[first_parent['parent']]

                index += 1
                intermediate[key]['index'] = index
                intermediate[key]['name'] = u', '.join([second_parent['display_name'], first_parent['display_name'],
                                                        val['display_name']])
                result.append(intermediate[key])

        return result


class CourseReportDownloadPresenter(CoursePresenter):
    """
    Presenter that can fetch temporary CSV download URLs from the data API
    """
    PROBLEM_RESPONSES = 'problem_response'

    def get_report_info(self, report_name):
        """
        Get a temporary download URL and status information such as the "last modified" date for
        a downloadable report.

        Does not check any permissions.

        Will raise NotFoundError if the course or the report does not exist.

        Example return value (only the first three fields are guaranteed; see API for details):
            {
              "course_id": "Example_Demo_2016-08",
              "report_name": "problem_response",
              "download_url": "https://bucket.s3.amazonaws.com/Example_Demo_2016-08_problem_response.csv?Signature=...",
              "last_modified": "2016-08-12T043411",
              "file_size": 3419,
              "expiration_date": "2016-08-12T233704",
            }
        """
        data = self.course.reports(report_name)
        for field in ('last_modified', 'expiration_date'):
            if field in data:
                data[field] = self.parse_api_datetime(data[field])
        return data
