from courses.presenters import BasePresenter
from django.core.cache import cache


class ProgramsPresenter(BasePresenter):
    """ Presenter for the programs metadata. """

    CACHE_KEY = 'programs'
    NON_NULL_STRING_FIELDS = ['program_id', 'program_type', 'program_title']

    @staticmethod
    def filter_programs(all_programs, program_ids=None, course_ids=None):
        """Filter results to just the program IDs specified and then to just the programs that have
           a course in the given course_ids list.
        """
        if program_ids is None:
            programs = all_programs
        else:
            programs = [program for program in all_programs if program['program_id'] in program_ids]

        # Now apply course_ids filter
        if course_ids is None:
            return programs
        return [program for program in programs if not set(program['course_ids']).isdisjoint(course_ids)]

    def _get_all_programs(self):
        """
        Returns all programs. If not cached, programs will be fetched
        from the analytics data API.
        """
        all_programs = cache.get(self.CACHE_KEY)
        if all_programs is None:
            all_programs = self.client.programs().programs()
            all_programs = [
                {field: ('' if val is None and field in self.NON_NULL_STRING_FIELDS else val)
                 for field, val in program.items()} for program in all_programs]
            cache.set(self.CACHE_KEY, all_programs)
        return all_programs

    def get_programs(self, program_ids=None, course_ids=None):
        """
        Returns programs that match those listed in program_ids.  If
        no program IDs provided, all programs will be returned.
        """
        all_programs = self._get_all_programs()
        filtered_programs = self.filter_programs(all_programs, program_ids=program_ids, course_ids=course_ids)

        # sort by title by default with blank values at the end
        filtered_programs = sorted(
            filtered_programs,
            key=lambda x: (not x['program_title'], x['program_title']))

        return filtered_programs
