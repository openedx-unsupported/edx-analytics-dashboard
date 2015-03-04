from unittest import TestCase

from common.course_structure import CourseStructure
from common.tests.factories import CourseStructureFactory


class CourseStructureTests(TestCase):
    def _prepare_assignments(self, structure, assignments):
        prepared = []

        for assignment in assignments:
            # Exclude assignments with invalid assignment types
            if not assignment['format']:
                continue

            problems = []
            for child in assignment.pop('children'):
                block = structure['blocks'][child]

                problems.append({
                    'id': block['id'],
                    'name': block['display_name']
                })

            prepared.append({
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'problems': problems,
            })

        return prepared

    def test_course_structure_to_assignments(self):
        factory = CourseStructureFactory()
        structure = factory.structure

        actual = CourseStructure.course_structure_to_assignments(structure, graded=True)
        expected = self._prepare_assignments(structure, factory.assignments)
        self.assertListEqual(actual, expected)

        # Test for assignment type filtering
        assignment_type = factory.grading_policy[0]['assignment_type']
        actual = CourseStructure.course_structure_to_assignments(structure, graded=True,
                                                                 assignment_type=assignment_type)
        assignments = [assignment for assignment in factory.assignments if assignment['format'] == assignment_type]
        expected = self._prepare_assignments(structure, assignments)
        self.assertListEqual(actual, expected)
