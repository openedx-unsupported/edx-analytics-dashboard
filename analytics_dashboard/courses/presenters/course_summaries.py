from django.core.cache import cache

from courses.presenters import BasePresenter


class CourseSummariesPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    CACHE_KEY = 'summaries'
    NON_NULL_STRING_FIELDS = ['course_id', 'catalog_course', 'catalog_course_title',
                              'start_date', 'end_date', 'pacing_type', 'availability']

    @staticmethod
    def filter_summaries(all_summaries, course_ids=None):
        """Filter results to just the course IDs specified."""
        if course_ids is None:
            return all_summaries
        else:
            return [summary for summary in all_summaries if summary['course_id'] in course_ids]

    def _get_all_summaries(self):
        """
        Returns all course summaries. If not cached, summaries will be fetched
        from the analytics data API.
        """
        all_summaries = cache.get(self.CACHE_KEY)
        if all_summaries is None:
            all_summaries = self.client.course_summaries().course_summaries()
            all_summaries = [
                {field: ('' if val is None and field in self.NON_NULL_STRING_FIELDS else val)
                 for field, val in summary.items()} for summary in all_summaries]
            cache.set(self.CACHE_KEY, all_summaries)
        return all_summaries

    def _get_last_updated(self, summaries):
        # all the create times should be the same, so just use the first one
        if summaries:
            summary = summaries[0]
            return self.parse_api_datetime(summary['created'])
        else:
            return None

    def get_course_summaries(self, course_ids=None):
        """
        Returns course summaries that match those listed in course_ids.  If
        no course IDs provided, all data will be returned.
        """
        all_summaries = self._get_all_summaries()
        filtered_summaries = self.filter_summaries(all_summaries, course_ids)

        # sort by title by default with "None" values at the end
        filtered_summaries = sorted(
            filtered_summaries,
            key=lambda x: (x['catalog_course_title'] is not None, x['catalog_course_title']))
        return filtered_summaries, self._get_last_updated(filtered_summaries)
