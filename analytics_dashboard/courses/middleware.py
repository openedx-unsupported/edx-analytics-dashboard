class CourseMiddleware(object):
    """
    Adds course info to the request object.
    """

    def process_view(self, request, _view_func, _view_args, view_kwargs):
        request.course_id = view_kwargs.get('course_id', None)
        return None
