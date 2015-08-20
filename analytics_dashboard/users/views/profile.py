import analyticsclient.constants
import dateutil.parser
from django.http import Http404

from .base import UsersView


class UserProfileView(UsersView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        try:
            username = kwargs['username']
        except ValueError:
            raise Http404

        response = self.client.users(username).profile()
        for date_field in ('last_login', 'date_joined'):
            if response[date_field]:
                response[date_field] = dateutil.parser.parse(response[date_field])
        context['profile'] = response
        context['constants'] = analyticsclient.constants

        return context
