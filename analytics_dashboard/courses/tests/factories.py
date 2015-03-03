import urllib

from common.tests.factories import CourseStructureFactory
from courses.tests.utils import CREATED_DATETIME_STRING


class CoursePerformanceDataFactory(CourseStructureFactory):
    """ Factory that can be used to generate data for course performance-related presenters and APIs. """

    def present_assignments(self):
        presented = []

        # Exclude assignments with no assignment type
        assignments = [assignment for assignment in self._assignments if assignment['format']]

        for assignment_index, assignment in enumerate(assignments):
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
                problems.append({
                    'index': problem_index + 1,
                    'total_submissions': problem_index,
                    'correct_submissions': problem_index,
                    'correct_percent': correct_percent,
                    'incorrect_submissions': 0.0,
                    'incorrect_percent': 0,
                    'id': _id,
                    'name': block['display_name'],
                    'part_ids': [part_id],
                    'url': urllib.quote(url_template.format(
                        CoursePerformanceDataFactory.course_id, assignment['id'], _id, part_id))
                })

            num_problems = len(problems)
            url_template = '/courses/{}/performance/graded_content/assignments/{}/'
            presented_assignment = {
                'index': assignment_index + 1,
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'problems': problems,
                'num_problems': num_problems,
                'total_submissions': num_problems,
                'correct_submissions': num_problems,
                'correct_percent': 1.0,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0,
                'url': urllib.quote(url_template.format(
                    CoursePerformanceDataFactory.course_id, assignment['id']))
            }

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
