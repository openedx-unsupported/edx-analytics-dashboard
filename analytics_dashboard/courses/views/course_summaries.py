import logging

from braces.views import LoginRequiredMixin

from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from courses import permissions
from courses.views import (
    CourseAPIMixin,
    LastUpdatedView,
    LazyEncoderMixin,
    TemplateView,
    TrackedViewMixin,
)
from courses.presenters.course_summaries import CourseSummariesPresenter


logger = logging.getLogger(__name__)


class CourseIndex(CourseAPIMixin, LoginRequiredMixin, TrackedViewMixin, LastUpdatedView, LazyEncoderMixin,
                  TemplateView):
    template_name = 'courses/index.html'
    page_title = _('Courses')
    page_name = {
        'scope': 'insights',
        'lens': 'home',
        'report': '',
        'depth': ''
    }
    # pylint: disable=line-too-long
    # Translators: Do not translate UTC.
    update_message = _('Course summary data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super(CourseIndex, self).get_context_data(**kwargs)
        courses = permissions.get_user_course_permissions(self.request.user)
        if not courses:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        presenter = CourseSummariesPresenter()

        summaries, last_updated = presenter.get_course_summaries(courses)
        context.update({
            'update_message': self.get_last_updated_message(last_updated)
        })

        data = {
            'course_list_json': summaries,
        }
        context['js_data']['course'] = data
        context['page_data'] = self.get_page_data(context)
        return context
