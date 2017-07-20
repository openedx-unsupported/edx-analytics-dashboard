from core.presenters import BasePresenter


class CourseSummariesPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    def get_course_summaries_response(self, course_ids=None, **kwargs):
        summaries_client = self.client.course_summaries()
        summaries_data = summaries_client.course_summaries(course_ids, **kwargs)
        summaries = summaries_data.get('results')
        last_updated = self._get_last_updated(summaries) if summaries else None
        return summaries_data, last_updated

    @classmethod
    def _get_last_updated(cls, summaries):
        # all the create times should be the same, so just use the first one
        if summaries:
            summary = summaries[0]
            return cls.parse_api_datetime(summary['created'])
        return None
