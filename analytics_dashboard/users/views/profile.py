import analyticsclient.constants
import dateutil.parser
from django.conf import settings
from django.http import Http404
from waffle import switch_is_active

from common.clients import EnrollmentApiClient
from .base import UsersView


def _parse_dates(dictionary, date_fields):
    """Parse textual dates in dictionary values to datetime objects."""
    for date_field in date_fields:
        if dictionary[date_field]:
            dictionary[date_field] = dateutil.parser.parse(dictionary[date_field])


class UserProfileView(UsersView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)

        try:
            username = kwargs['username']
        except ValueError:
            raise Http404

        profile = self.client.users(username).profile()
        _parse_dates(profile, ['last_login', 'date_joined'])

        enrollment_api = EnrollmentApiClient(settings.ENROLLMENT_API_URL, self.request.user.access_token)
        enrollments = enrollment_api.enrollment.get(user=profile['username'])
        for enrollment in enrollments:
            course_details = enrollment['course_details']
            _parse_dates(enrollment, ['created'])
            _parse_dates(course_details, ['course_start', 'course_end'])
            if switch_is_active('display_names_for_course_index'):
                course_details['name'] = self.get_course_info(course_details['course_id'])['name']

        context['profile'] = profile
        context['enrollments'] = enrollments
        context['constants'] = analyticsclient.constants

        return context
