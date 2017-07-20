from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.http import JsonResponse

from courses import permissions

from .presenters import CourseSummariesPresenter

class CourseSummariesAPIView(View):

    list_params = set(['availability', 'pacing_type', 'program_ids'])
    string_params = set(['text_search', 'sortKey', 'order'])
    int_params = set(['page', 'page_size'])

    def get(self, request):
        kwargs = {}

        course_ids = permissions.get_user_course_permissions(self.request.user)
        if not course_ids:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied
        kwargs['course_ids'] = course_ids

        get_keys = set(request.GET.keys())
        for list_param in self.list_params & get_keys:
            kwargs[list_param] = request.GET.get(list_param).split(',')
        for string_param in self.string_params & get_keys:
            kwargs[string_param] = request.GET.get(string_param)
        for int_param in self.int_params & get_keys:
            try:
                kwargs[int_param] = int(request.GET.get(int_param))
            except ValueError:
                pass

        # Handle the one parameter that doesn't follow snake case...
        if 'sortKey' in kwargs:
            kwargs['sort_key'] = kwargs['sortKey']
            del kwargs['sortKey']

        raw_summaries_data, last_updated = (
            CourseSummariesPresenter().get_course_summaries_response(**kwargs)
        )
        summaries_data = raw_summaries_data.copy()
        if last_updated:
            summaries_data['last_updated'] = last_updated

        return JsonResponse(summaries_data)
