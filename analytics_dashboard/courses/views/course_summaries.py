from braces.views import LoginRequiredMixin
import logging

from django.core.exceptions import PermissionDenied

from courses import permissions
from courses.views import (
    CourseAPIMixin,
    LazyEncoderMixin,
    TemplateView,
    TrackedViewMixin,
)
from courses.presenters.course_summaries import CourseSummariesPresenter


logger = logging.getLogger(__name__)


class CourseIndex(CourseAPIMixin, LoginRequiredMixin, TrackedViewMixin, LazyEncoderMixin, TemplateView):
    template_name = 'courses/index.html'
    page_name = {
        'scope': 'insights',
        'lens': 'home',
        'report': '',
        'depth': ''
    }

    def get_context_data(self, **kwargs):
        courses = permissions.get_user_course_permissions(self.request.user)
        if not courses:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        self.presenter = CourseSummariesPresenter()

        context = super(CourseIndex, self).get_context_data(**kwargs)
        data = {
            # TODO: this is not needed
            'course_list_url': 'http://example.com',
            'course_list_json': self.presenter.get_course_summaries(courses),
        }
        context['js_data']['course'] = data
        context['page_data'] = self.get_page_data(context)
        return context
