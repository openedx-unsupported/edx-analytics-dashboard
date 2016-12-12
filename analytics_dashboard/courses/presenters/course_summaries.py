from courses.presenters import BasePresenter

NON_NULL_STRING_FIELDS = ['course_id', 'catalog_course', 'catalog_course_title', 'start_date', 'end_date',
                          'pacing_type', 'availability']


class CourseSummariesPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    def get_course_summaries(self, course_ids=None):

        # TODO: cache results
        # TODO: what happens w/ a 404
        api_response = self.client.course_summaries().course_summaries()
        # TODO: need to filter the responses so that only the ones that match our
        # specified courses are returned and we fill in the blanks too in case we
        # don't have data

        api_response = [{field: ('' if val is None and field in NON_NULL_STRING_FIELDS else val)
                         for field, val in summary.items()}
                        for summary in api_response]

        # By default, sort summaries by enrollment count descending
        api_response = sorted(api_response, key=lambda summary: summary['count'], reverse=True)
        return api_response
