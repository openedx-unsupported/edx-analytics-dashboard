from unittest import TestCase

from common.course_structure import CourseStructure
from common.tests.factories import CourseStructureFactory


class CourseStructureTests(TestCase):
    def _prepare_structure(self, structure, assignments, has_format=True):
        prepared = []

        for assignment in assignments:
            # Exclude assignments with invalid assignment types
            if has_format:
                if not assignment['format']:
                    continue

            problems = []
            for child in assignment.pop('children'):
                block = structure['blocks'][child]
                child_block = {
                    'id': block['id'],
                    'name': block['display_name']
                }
                problems.append(child_block)

                grandchildren = []
                for grandchild in block['children']:
                    block = structure['blocks'][grandchild]
                    grandchildren.append({
                        'id': block['id'],
                        'name': block['display_name'],
                        'children': []
                    })
                if grandchildren:
                    child_block['children'] = grandchildren

            block = {
                'id': assignment['id'],
                'name': assignment['display_name'],
                'children': problems,
            }

            if has_format:
                block['assignment_type'] = assignment['format']

            prepared.append(block)

        return prepared

    def test_course_structure_to_assignments(self):
        factory = CourseStructureFactory()
        structure = factory.structure

        actual = CourseStructure.course_structure_to_assignments(structure, graded=True)
        expected = self._prepare_structure(structure, factory.assignments)
        self.assertListEqual(actual, expected)

        # Test for assignment type filtering
        assignment_type = factory.grading_policy[0]['assignment_type']
        actual = CourseStructure.course_structure_to_assignments(structure, graded=True,
                                                                 assignment_type=assignment_type)
        assignments = [assignment for assignment in factory.assignments if assignment['format'] == assignment_type]
        expected = self._prepare_structure(structure, assignments)
        self.assertListEqual(actual, expected)

    def test_course_structure_to_sections(self):
        factory = CourseStructureFactory()
        structure = factory.structure

        actual = CourseStructure.course_structure_to_sections(structure, 'problem', False)
        self.assertListEqual(actual, self._prepare_structure(structure, factory.sections, False))
