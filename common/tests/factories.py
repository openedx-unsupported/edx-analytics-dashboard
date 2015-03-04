import copy
import uuid


class CourseStructureFactory(object):
    """ Factory that can be used to generate course structure. """

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

        # Add invalid data that should be filtered out by consuming code
        self._assignments.append(self._generate_block('sequential', None, 'Block with no format', graded=True))
        self._assignments.append(self._generate_block('sequential', '', 'Block with format set to empty string', graded=True))

    @property
    def structure(self):
        return copy.deepcopy(self._structure)

    @property
    def assignments(self):
        return copy.deepcopy(self._assignments)
