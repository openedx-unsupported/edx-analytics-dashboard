import copy
import uuid


class CourseStructureFactory(object):
    """ Factory that can be used to generate course structure. """

    assignment_types = ['Homework', 'Exam']
    _course_id = "edX/DemoX/Demo_Course"
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
        },
        {
            "assignment_type": "",
            "count": 4,
            "dropped": 0,
            "weight": 0
        },
        {
            "assignment_type": None,
            "count": 1,
            "dropped": 0,
            "weight": 0
        }
    ]

    _count_of_problems = 4

    def __init__(self):
        self._structure = {}
        self._assignments = []
        self._sections = []
        self._subsections = []
        self._ungraded_problems = []
        self._subsection_children = []
        self._generate_structure()

    @property
    def course_id(self):
        return self._course_id

    @course_id.setter
    def course_id(self, course_id):
        self._course_id = course_id

    def _get_block_id(self, block_type, block_format=None, display_name=None,  # pylint: disable=unused-argument
                      graded=True, children=None):                             # pylint: disable=unused-argument
        return uuid.uuid4().hex

    def _generate_block(self, block_type, block_format=None, display_name=None, graded=True, children=None):
        return {
            'id': 'i4x://edX/DemoX/{}/{}'.format(block_type, self._get_block_id(block_type, block_format, display_name,
                                                                                graded, children)),
            'display_name': display_name,
            'graded': graded,
            'format': block_format,
            'type': block_type,
            'children': children or []
        }

    def _generate_subsection_children(self, assignment_type, display_name, problem_index, graded):
        """ Overwrite if you want other subsection types (e.g. videos) """
        problem = self._generate_block('problem',
                                       assignment_type,
                                       '{} Problem {}'.format(display_name, problem_index),
                                       graded)
        self._structure['blocks'][problem['id']] = problem
        return problem

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
        blocks = self._structure['blocks']

        self._assignments = []
        for gp in self._cleaned_grading_policy:
            count = gp['count']
            assignment_type = gp['assignment_type']

            for assignment_index in range(1, count + 1):
                display_name = '{} {}'.format(assignment_type, assignment_index)
                graded_children = []

                # Generate the graded children
                for problem_index in range(1, self._count_of_problems):
                    problem = self._generate_subsection_children(assignment_type, display_name, problem_index, True)
                    graded_children.append(problem['id'])

                assignment = self._generate_block('sequential', assignment_type, display_name, children=graded_children)
                assignment_id = assignment['id']
                blocks[assignment_id] = assignment
                blocks[root]['children'].append(assignment_id)
                self._assignments.append(assignment)

        # Add invalid data that should be filtered out by consuming code
        self._assignments.append(self._generate_block('sequential', None, 'Block with no format'))
        self._assignments.append(self._generate_block('sequential', '', 'Block with format set to empty string'))

        # add ungraded
        self._subsection_children = [self._generate_subsection_children(None, 'Ungraded Problem', 1, False)]

        self._subsections = [self._generate_block('sequential', None, 'Subsection 1', False,
                                                  [self._subsection_children[0]['id']])]
        blocks[self._subsections[0]['id']] = self._subsections[0]

        section = self._generate_block('chapter', None, 'Chapter 1', False, [self._subsections[0]['id']])
        section_id = section['id']
        self._sections = [section]
        blocks[section_id] = section
        blocks[root]['children'].append(section_id)

    @property
    def structure(self):
        return copy.deepcopy(self._structure)

    @property
    def assignments(self):
        return copy.deepcopy(self._assignments)

    @property
    def sections(self):
        return copy.deepcopy(self._sections)

    @property
    def subsections(self):
        return copy.deepcopy(self._subsections)

    @property
    def _cleaned_grading_policy(self):
        return [item for item in self.grading_policy if item['assignment_type']]
