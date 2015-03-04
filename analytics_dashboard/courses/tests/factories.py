import copy
import urllib
import uuid

from courses.tests.utils import CREATED_DATETIME_STRING


class CoursePerformanceDataFactory(object):
    """ Factory that can be used to generate data for course performance-related presenters and APIs. """

    course_id = "edX/DemoX/Demo_Course"
    assignment_types = ['Homework', 'Exam']
    grading_policy = [
        {
            "assignment_type": "Homework",
            "count": 5,
            "dropped": 1,
            "weight": 0.2
        },
        {
            "assignment_type": "Exam",
            "count": 4,
            "dropped": 0,
            "weight": 0.8
        }
    ]

    def __init__(self):
        self._structure = {}
        self._assignments = []
        self._generate_structure()

    def _generate_block(self, block_type, block_format=None, display_name=None, graded=True, children=None):
        return {
            'id': 'i4x://edX/DemoX/{}/{}'.format(block_type, uuid.uuid4().hex),
            'display_name': display_name,
            'graded': graded,
            'format': block_format,
            'type': block_type,
            'children': children or []
        }

    def _generate_structure(self):
        root = 'i4x://edX/DemoX/course/Demo_Course'
        self._structure = {
            'root': root,
            'blocks': {
                root: {
                    'id': root,
                    'display_name': 'Demo Course',
                    'graded': False,
                    'format': None,
                    'type': 'course',
                    'children': []
                }
            }
        }

        self._assignments = []
        for gp in self.grading_policy:
            count = gp['count']
            assignment_type = gp['assignment_type']
            for assignment_index in range(1, count + 1):
                display_name = '{} {}'.format(assignment_type, assignment_index)
                children = []

                # Generate the children
                for problem_index in range(1, 4):
                    problem = self._generate_block('problem',
                                                   assignment_type,
                                                   '{} Problem {}'.format(display_name, problem_index))
                    problem_id = problem['id']
                    children.append(problem_id)
                    self._structure['blocks'][problem_id] = problem

                assignment = self._generate_block('sequential', assignment_type, display_name, children=children)
                assignment_id = assignment['id']
                self._structure['blocks'][assignment_id] = assignment
                self._structure['blocks'][root]['children'].append(assignment_id)

                self._assignments.append(assignment)

    def present_assignments(self, include_submissions=True):
        presented = []

        for assignment_index, assignment in enumerate(self._assignments):
            problems = []
            for problem_index, child in enumerate(assignment['children']):
                block = self._structure['blocks'][child]

                _id = block['id']
                part_id = '{}_1_2'.format(_id)
                correct_percent = 1.0
                if problem_index == 0:
                    correct_percent = 0
                url_template = '/courses/{}/performance/graded_content/assignments/{}/problems/' \
                               '{}/parts/{}/answer_distribution/'

                problem = {
                    'index': problem_index + 1,
                    'id': _id,
                    'name': block['display_name'],
                    'total_submissions': 0,
                    'correct_submissions': 0,
                    'correct_percent': 0,
                    'incorrect_submissions': 0,
                    'incorrect_percent': 0,
                    'part_ids': []
                }

                if include_submissions:
                    problem.update({
                        'part_ids': [part_id],
                        'total_submissions': problem_index,
                        'correct_submissions': problem_index,
                        'correct_percent': correct_percent,
                        'incorrect_submissions': 0,
                        'incorrect_percent': 0,
                        'url': urllib.quote(url_template.format(self.course_id, assignment['id'], _id, part_id)),
                    })

                problems.append(problem)

            num_problems = len(problems)
            url_template = '/courses/{}/performance/graded_content/assignments/{}/'
            total_submissions = sum([problem['total_submissions'] for problem in problems])
            correct_submissions = sum([problem['correct_submissions'] for problem in problems])
            presented_assignment = {
                'index': assignment_index + 1,
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'problems': problems,
                'num_problems': num_problems,
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions,
                'correct_percent': 0.0 if not total_submissions else correct_submissions / total_submissions,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0
            }

            if total_submissions > 0:
                presented_assignment['url'] = urllib.quote(url_template.format(self.course_id, assignment['id']))

            presented.append(presented_assignment)

        return presented

    def problems(self):
        problems = []

        for assignment in self._assignments:
            for index, problem in enumerate(assignment['children']):
                problem = self._structure['blocks'][problem]
                problems.append({
                    "module_id": problem["id"],
                    "total_submissions": index,
                    "correct_submissions": index,
                    "part_ids": ["{}_1_2".format(problem["id"])],
                    "created": CREATED_DATETIME_STRING
                })

        return problems

    @property
    def structure(self):
        return copy.deepcopy(self._structure)

    @property
    def assignments(self):
        return copy.deepcopy(self._assignments)
