from requests.auth import AuthBase


class CourseStructure(object):
    @staticmethod
    def _filter_children(blocks, key, **kwargs):
        """
        Given the blocks locates the nested graded or ungraded problems.
        """
        block = blocks[key]

        block_type = kwargs.pop(u'block_type', None)
        if block_type:
            kwargs[u'type'] = block_type

        kwargs.setdefault(u'graded', False)

        matched = True
        for name, value in kwargs.iteritems():
            matched &= (block.get(name, None) == value)
            if not matched:
                break

        if matched:
            return [block]

        children = []
        for child in block[u'children']:
            children += CourseStructure._filter_children(blocks, child, **kwargs)

        return children

    @staticmethod
    def course_structure_to_assignments(structure, graded=None, assignment_type=None):
        """
        Returns the assignments and nested problems from the given course structure.
        """

        blocks = structure[u'blocks']
        root = blocks[structure[u'root']]

        # Break down the course structure into assignments and nested problems, returning only the data
        # we absolutely need.
        assignments = []

        kwargs = {
            'graded': graded
        }

        if assignment_type:
            kwargs[u'format'] = assignment_type

        filtered = CourseStructure._filter_children(blocks, root[u'id'], **kwargs)

        for assignment in filtered:
            filtered_children = CourseStructure._filter_children(blocks, assignment[u'id'], graded=graded,
                                                                 block_type=u'problem')
            problems = []
            for problem in filtered_children:
                problems.append({
                    'id': problem['id'],
                    'name': problem['display_name'],
                    'total_submissions': 0,
                    'correct_submissions': 0,
                    'incorrect_submissions': 0,
                })

            assignments.append({
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'problems': problems,
            })

        return assignments


class BearerAuth(AuthBase):
    """ Attaches Bearer Authentication to the given Request object. """

    def __init__(self, token):
        """ Instantiate the auth class. """
        self.token = token

    def __call__(self, r):
        """ Update the request headers. """
        r.headers['Authorization'] = 'Bearer {0}'.format(self.token)
        return r
