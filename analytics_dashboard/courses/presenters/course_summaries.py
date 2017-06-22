from waffle import switch_is_active

from courses.presenters import BasePresenter


class CourseSummariesPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    NON_NULL_STRING_FIELDS = ['course_id', 'catalog_course', 'catalog_course_title',
                              'start_date', 'end_date', 'pacing_type', 'availability']

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

        # sort by title by default with "None" values at the end
        summaries = sorted(
            summaries,
            key=lambda x: (not x['catalog_course_title'], x['catalog_course_title'])
        )

        return summaries, self._get_last_updated(summaries)

    def get_course_summary_metrics(self, summaries):
        summary = {
            'total_enrollment': reduce(lambda x, y: x + y.get('cumulative_count', 0), summaries, 0),
            'current_enrollment': reduce(lambda x, y: x + y.get('count', 0), summaries, 0),
            'enrollment_change_7_days': reduce(lambda x, y: x + y.get('count_change_7_days', 0), summaries, 0),
            'verified_enrollment': reduce(lambda x, y: x + y.get('enrollment_modes', {}).get('verified',
                                                                                             {}).get('count', 0),
                                          summaries, 0),
        }

        return summary
