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
                'children': problems,
                'num_children': num_problems,
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

    def problems(self, graded=True):
        problems = []
        parents = self._assignments if graded else self._subsections

        for assignment in parents:
            for index, problem in enumerate(assignment['children']):
                num_submissions = index if graded else 1
                problem = self._structure['blocks'][problem]
                problems.append({
                    "module_id": problem["id"],
                    "total_submissions": num_submissions,
                    "correct_submissions": num_submissions,
                    "part_ids": ["{}_1_2".format(problem["id"])],
                    "created": CREATED_DATETIME_STRING
                })

        return problems

    @property
    def present_grading_policy(self):
        return self._cleaned_grading_policy

    @property
    def present_assignment_types(self):
        policies = self._cleaned_grading_policy
        return [{'name': gp['assignment_type']} for gp in policies]

    @property
    def present_sections(self):
        presented = []
        total_submissions = 1

        for section_index, section in enumerate(self._sections):
            subsections = []
            for subsection_index, subsection in enumerate(self._subsections):
                problems = []
                for problem_index, child in enumerate(subsection['children']):
                    block = self._structure['blocks'][child]

                    _id = block['id']
                    part_id = '{}_1_2'.format(_id)
                    correct_percent = 1.0
                    url_template = '/courses/{}/performance/ungraded_content/sections/{}/subsections/' \
                                   '{}/problems/{}/parts/{}/answer_distribution/'
                    problems.append({
                        'index': problem_index + 1,
                        'total_submissions': total_submissions,
                        'correct_submissions': total_submissions,
                        'correct_percent': correct_percent,
                        'incorrect_submissions': 0.0,
                        'incorrect_percent': 0,
                        'id': _id,
                        'name': block['display_name'],
                        'part_ids': [part_id],
                        'children': [],
                        'url': urllib.quote(url_template.format(
                            CoursePerformanceDataFactory.course_id, section['id'],
                            subsection['id'], _id, part_id))
                    })

                num_problems = len(problems)
                url_template = '/courses/{}/performance/ungraded_content/sections/{}/subsections/{}/'
                presented_subsection = {
                    'index': subsection_index + 1,
                    'id': subsection['id'],
                    'name': subsection['display_name'],
                    'children': problems,
                    'num_children': num_problems,
                    'total_submissions': num_problems,
                    'correct_submissions': num_problems,
                    'correct_percent': 1.0,
                    'incorrect_submissions': 0,
                    'incorrect_percent': 0.0,
                    'url': urllib.quote(url_template.format(
                        CoursePerformanceDataFactory.course_id, section['id'],
                        subsection['id']))
                }
                subsections.append(presented_subsection)

            num_problems = 1
            url_template = '/courses/{}/performance/ungraded_content/sections/{}/'
            presented_sections = {
                'index': section_index + 1,
                'id': section['id'],
                'name': section['display_name'],
                'children': subsections,
                'num_children': num_problems,
                'total_submissions': num_problems,
                'correct_submissions': num_problems,
                'correct_percent': 1.0,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0,
                'url': urllib.quote(url_template.format(
                    CoursePerformanceDataFactory.course_id, section['id']))
            }

            presented.append(presented_sections)

        return presented
