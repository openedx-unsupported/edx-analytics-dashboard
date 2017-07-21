from django.core.exceptions import PermissionDenied
#from django.views.generic import View
#from django.http import JsonResponse

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from courses import permissions

from .presenters import CourseSummariesPresenter


class CourseSummariesAPIView(RetrieveAPIView):

    list_params = set(['availability', 'pacing_type', 'program_ids'])
    string_params = set(['text_search', 'order_by', 'sort_order'])
    int_params = set(['page', 'page_size'])

    def get(self, request):
        kwargs = {}

        course_ids = permissions.get_user_course_permissions(self.request.user)
        if not course_ids:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied
        kwargs['course_ids'] = None #course_ids

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

        # @@TODO better handle these inconsistencies
        if 'order_by' in kwargs:
            kwargs['sort_key'] = kwargs['order_by']
            del kwargs['order_by']
        if 'sort_order' in kwargs:
            kwargs['order'] = kwargs['sort_order']
            del kwargs['sort_order']

        summaries_data = (
            CourseSummariesPresenter().get_course_summaries_response(**kwargs)
        )
        return Response(data=summaries_data, status=200)
