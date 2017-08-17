from courses.presenters import BasePresenter


class CourseTotalsDataPresenter(BasePresenter):
    """
    Total enrollment statistics across multiple courses.
    """

    def get_course_totals(self, course_ids=None):
        """
        Get course totals.

        Arguments:
            course_ids (list[str]|NoneType): Course IDs to filter by.

        Returns: dict, with following key/value pairs:
            count: Total number of learners currently enrolled in the specified courses.
            cumulative_count: Total number of learners ever enrolled in the specified courses.
            count_change_7_days: Total change in enrollment across specified courses.
            verified_enrollment: Total number of leaners currently enrolled as verified in specified courses.
        """
        return self.client.course_totals().course_totals(course_ids)
