from courses.presenters import BasePresenter


class CourseAggregateDataPresenter(BasePresenter):

    def get_course_aggregate_data(self, course_ids=None):
        return self.client.course_totals().course_totals(
            course_ids
        )
