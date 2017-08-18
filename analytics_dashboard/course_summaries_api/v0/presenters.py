from core.presenters import BasePresenter


class CourseSummariesPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    def get_course_summaries_page(self, course_ids=None, **kwargs):
        """
        Retrieves a page of course summaries.

        Arguments:
            course_ids (list[str]): List of course ID strings of summaries to retrieve.
            **kwargs (dict): All other arguments to be passed to API client.

        Returns: dict, with the following key/value pairs:
            count (int): Total number of results across all pages.
            next (str): If not last page, URL to next page.
            prev (str): If not first page, URL to previous page.
            results (list[dict]): Course summaries. See API documentation for schema.
            last_updated (datetime): When course summaries were last updated.
        """
        summaries_client = self.client.course_summaries()
        summaries_page = summaries_client.course_summaries(course_ids, **kwargs)
        summaries = summaries_page.get('results')
        last_updated = self._get_last_updated(summaries) if summaries else None
        summaries_page.update({'last_updated': last_updated})
        return summaries_page

    def get_course_summaries_unpaginated(self, course_ids=None, **kwargs):
        """
        Retrieves all pages of course summaries.
        Only use this for the CSV!

        Arguments:
            course_ids (list[str]): List of course ID strings of summaries to retrieve.
            **kwargs (dict): All other arguments to be passed to API client.

        Returns: list[dict]
            List of course summary dicts. See API documentation for schema.
        """
        summaries_client = self.client.course_summaries()
        return summaries_client.course_summaries(course_ids, request_all=True, **kwargs)

    @classmethod
    def _get_last_updated(cls, summaries):
        # all the create times should be the same, so just use the first one
        if summaries:
            summary = summaries[0]
            return cls.parse_api_datetime(summary['created'])
        return None
