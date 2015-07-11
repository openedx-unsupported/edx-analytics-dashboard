from __future__ import division
from django.http import Http404
import math

from .base import UsersView


class UserListView(UsersView):
    template_name = 'users/list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)

        # TODO: Check permissions of self.request.user

        users_per_page = 100
        try:
            page = int(self.request.GET.get('page', 1))
            if page < 1:
                raise ValueError
        except ValueError:
            raise Http404

        response = self.client.user_list().list_users(page=page, limit=users_per_page)
        users_count = response['count']
        context['count'] = users_count
        context['page'] = page
        context['total_pages'] = int(math.ceil(users_count / users_per_page))
        context['users'] = response['results']

        return context
