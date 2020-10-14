class CourseStructure:
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

        block_type = kwargs.pop('block_type', None)
        if block_type:
            kwargs['type'] = block_type

        matched = True
        for name, value in kwargs.items():
            matched &= (block.get(name, None) == value)
            if not matched:
                break

        if matched:
            if require_format:
                if 'format' in block and block['format']:
                    return [block]
            else:
                return [block]

        children = []
        if 'children' in block:
            for child in block['children']:
                children += CourseStructure._filter_children(blocks, child, require_format=require_format, **kwargs)

        return children

    @staticmethod
    def course_structure_to_assignments(structure, graded=None, assignment_type=None):
        """
        Returns the assignments and nested problems from the given course structure.
        """

        blocks = structure['blocks']
        root = blocks[structure['root']]

        # Break down the course structure into assignments and nested problems, returning only the data
        # we absolutely need.
        assignments = []

        kwargs = {
            'graded': graded
        }

        if assignment_type:
            kwargs['format'] = assignment_type

        filtered = CourseStructure._filter_children(blocks, root['id'], require_format=True, **kwargs)

        for assignment in filtered:
            filtered_children = CourseStructure._filter_children(blocks, assignment['id'], graded=graded,
                                                                 block_type='problem', require_format=False)
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
                'children': problems,
            })

        return assignments

    @staticmethod
    def course_structure_to_sections(structure, child_block_type, graded=None):
        """
        Returns sections, subsections, and the child block type (e.g. problem or video), nested
        within 'children' attributes.
        """

        blocks = structure['blocks']
        root = blocks[structure['root']]
        sections = CourseStructure._build_sections(blocks, root['id'],
                                                   graded, ['chapter', 'sequential', str(child_block_type)])
        return sections

    @staticmethod
    def _build_sections(blocks, section_id, graded, block_types):
        """ Recursively build sections of block_type. """
        sections = []
        if block_types:
            block_types = list(block_types)
            block_type = block_types.pop(0)
            filter_kwargs = {
                'block_type': block_type,
            }
            if graded is not None:
                filter_kwargs['graded'] = graded
            structure_sections = CourseStructure._filter_children(blocks, section_id,
                                                                  require_format=False,
                                                                  **filter_kwargs)

            for section in structure_sections:
                children = CourseStructure._build_sections(blocks, section['id'], graded, block_types)
                sections.append({
                    'id': section['id'],
                    'name': section['display_name'],
                    'children': children
                })

        return sections
