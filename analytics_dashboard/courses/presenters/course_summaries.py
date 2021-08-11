from analyticsclient.constants import enrollment_modes
from django.conf import settings
from django.core.cache import cache
from waffle import switch_is_active

from analytics_dashboard.courses.presenters import BasePresenter


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
        return [summary for summary in all_summaries if summary['course_id'] in course_ids]

    def _get_summaries(self, course_ids=None):
        """Returns list of course summaries.

        If requesting full list and it's not cached or requesting a subset of course_summaries with the course_ids
        parameter, summaries will be fetched from the analytics data API.
        """
        summaries = None
        if course_ids is None:
            # we only cache the full list of summaries
            summaries = cache.get(self.CACHE_KEY)
        if summaries is None:
            exclude = ['programs']  # we make a separate call to the programs endpoint
            if not switch_is_active('enable_course_passing'):
                exclude.append('passing_users')
            summaries = self.client.course_summaries().course_summaries(course_ids=course_ids, exclude=exclude)
            summaries = [
                {
                    field: (
                        '' if val is None and field in self.NON_NULL_STRING_FIELDS
                        else val
                    )
                    for field, val in summary.items()
                } for summary in summaries
            ]
            if course_ids is None:
                cache.set(self.CACHE_KEY, summaries, settings.COURSE_SUMMARIES_CACHE_TIMEOUT)
        return summaries

    def _get_last_updated(self, summaries):
        # all the create times should be the same, so just use the first one
        if summaries:
            summary = summaries[0]
            return self.parse_api_datetime(summary['created'])
        return None

    def get_course_summaries(self, course_ids=None):
        """
        Returns course summaries that match those listed in course_ids.  If
        no course IDs provided, all data will be returned.
        """
        if course_ids and len(course_ids) > settings.COURSE_SUMMARIES_IDS_CUTOFF:
            # Request all courses from the Analytics API and filter here
            all_summaries = self._get_summaries()
            summaries = self.filter_summaries(all_summaries, course_ids)
        else:
            # Request courses only in ID list from the Analytics API
            summaries = self._get_summaries(course_ids=course_ids)

        # sort by title by default with "None" values at the end
        summaries = sorted(
            summaries,
            key=lambda x: (not x['catalog_course_title'], x['catalog_course_title']))

        return summaries, self._get_last_updated(summaries)

    def get_course_summary_metrics(self, summaries):
        total = 0
        current = 0
        week_change = 0
        verified = 0
        masters = 0
        for s in summaries:
            total += s.get('cumulative_count', 0)
            current += s.get('count', 0)
            week_change += s.get('count_change_7_days', 0)
            modes = s.get('enrollment_modes', {})
            verified += modes.get(enrollment_modes.VERIFIED, {}).get('count', 0)
            masters += modes.get(enrollment_modes.MASTERS, {}).get('count', 0)

        summary = {
            'total_enrollment': total,
            'current_enrollment': current,
            'enrollment_change_7_days': week_change,
            'verified_enrollment': verified,
            'masters_enrollment': masters,
        }

        return summary
