class CourseStructure(object):
    @staticmethod
    def _filter_children(blocks, key, require_format=False, **kwargs):
        """
        Given the blocks, locates the nested blocks matching the criteria set in kwargs.

        Arguments
            blocks          --   Dictionary mapping ID strings to block dicts
            key             --   ID of the root node where tree traversal should begin
            require_format  --   Boolean indicating if the format field should be required to have a
                                 non-empty (truthy) value if a match is made
            kwargs          --   Dictionary mapping field names to required values for matches
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
            if require_format:
                if block[u'format']:
                    return [block]
            else:
                return [block]

        children = []
        for child in block[u'children']:
            children += CourseStructure._filter_children(blocks, child, require_format=require_format, **kwargs)

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

        filtered = CourseStructure._filter_children(blocks, root[u'id'], require_format=True, **kwargs)

        for assignment in filtered:
            filtered_children = CourseStructure._filter_children(blocks, assignment[u'id'], graded=graded,
                                                                 block_type=u'problem', require_format=False)
            problems = []
            for problem in filtered_children:
                problems.append({
                    'id': problem['id'],
                    'name': problem['display_name']
                })

            assignments.append({
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'problems': problems,
            })

        return assignments
