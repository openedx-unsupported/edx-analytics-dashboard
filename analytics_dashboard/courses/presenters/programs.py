from courses.presenters import BasePresenter
from django.core.cache import cache


class ProgramsPresenter(BasePresenter):
    """ Presenter for the programs metadata. """

    CACHE_KEY = 'programs3'
    NON_NULL_STRING_FIELDS = ['program_id', 'program_type', 'program_title']

    @staticmethod
    def filter_programs(all_programs, program_ids=None):
        """Filter results to just the program IDs specified."""
        if program_ids is None:
            return all_programs
        else:
            return [program for program in all_programs if program['program_id'] in program_ids]

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

    def get_programs(self, program_ids=None):
        """
        Returns programs that match those listed in program_ids.  If
        no program IDs provided, all programs will be returned.
        """
        all_programs = self._get_all_programs()
        filtered_programs = self.filter_programs(all_programs, program_ids)

        # sort by title by default with "None" values at the end
        filtered_programs = sorted(
            filtered_programs,
            key=lambda x: (not x['program_title'], x['program_title']))

        return filtered_programs
