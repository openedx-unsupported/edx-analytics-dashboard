from courses.presenters import BasePresenter


class CourseSummariesPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    def get_course_summaries(self, course_ids=None):

        # TODO: cache results
        # TODO: what happens w/ a 404
        api_response = self.client.course_summaries().course_summaries()
        # TODO: need to filter the responses so that only the ones that match our
        # specified courses are returned and we fill in the blanks too in case we
        # don't have data

        return api_response
