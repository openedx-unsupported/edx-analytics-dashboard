import logging

from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework_csv.renderers import CSVRenderer
from waffle import switch_is_active

from analytics_dashboard.core.utils import remove_keys
from analytics_dashboard.courses import permissions
from analytics_dashboard.courses.presenters.course_summaries import CourseSummariesPresenter
from analytics_dashboard.courses.presenters.programs import ProgramsPresenter
from analytics_dashboard.courses.views import (
    CourseAPIMixin,
    LastUpdatedView,
    LazyEncoderMixin,
    TemplateView,
    TrackedViewMixin,
    AnalyticsV1Mixin,
)
from analytics_dashboard.courses.views.csv import DatetimeCSVResponseMixin

logger = logging.getLogger(__name__)


class CourseIndex(AnalyticsV1Mixin, CourseAPIMixin, LoginRequiredMixin, TrackedViewMixin, LastUpdatedView,
                  LazyEncoderMixin, TemplateView):
    template_name = 'courses/index.html'
    page_title = _('Courses')
    page_name = {
        'scope': 'insights',
        'lens': 'home',
        'report': '',
        'depth': ''
    }
    # Translators: Do not translate UTC.
    update_message = _('Course summary data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        courses = permissions.get_user_course_permissions(user)
        if not courses and not (user.is_superuser or user.is_staff):
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        summaries_presenter = CourseSummariesPresenter(analytics_client=self.analytics_client)
        summaries, last_updated = summaries_presenter.get_course_summaries(courses)

        context.update({
            'update_message': self.get_last_updated_message(last_updated)
        })

        enable_course_filters = switch_is_active('enable_course_filters')
        data = {
            'course_list_json': summaries,
            'enable_course_filters': enable_course_filters,
            'enable_passing_users': switch_is_active('enable_course_passing'),
            'course_list_download_url': reverse('courses:index_csv'),
        }

        if enable_course_filters:
            programs_presenter = ProgramsPresenter(analytics_client=self.analytics_client)
            programs = programs_presenter.get_programs(course_ids=courses)
            data['programs_json'] = programs

        context['js_data']['course'] = data
        context['page_data'] = self.get_page_data(context)
        context['summary'] = summaries_presenter.get_course_summary_metrics(summaries)

        return context


class CourseIndexCSV(AnalyticsV1Mixin, CourseAPIMixin, LoginRequiredMixin, DatetimeCSVResponseMixin, TemplateView):

    csv_filename_suffix = 'course-list'
    # Note: we are not using the DRF "renderer_classes" field here because this is a Django view, not a DRF view.
    # We will call the render function on the renderer directly instead.
    renderer = CSVRenderer()
    exclude_fields = {
        '': ('created',),
        'enrollment_modes': {
            'audit': ('count_change_7_days',),
            'credit': ('count_change_7_days',),
            'honor': ('count_change_7_days',),
            'professional': ('count_change_7_days',),
            'verified': ('count_change_7_days',),
            'masters': ('count_change_7_days',),
        }
    }

    def get_data(self):
        user = self.request.user
        courses = permissions.get_user_course_permissions(user)
        if not courses and not (user.is_superuser or user.is_staff):
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        enable_course_filters = switch_is_active('enable_course_filters')

        presenter = CourseSummariesPresenter(analytics_client=self.analytics_client)
        summaries, _ = presenter.get_course_summaries(courses)

        if not summaries:
            # Instead of returning a useless blank CSV, return a 404 error
            raise Http404

        # Exclude specified fields from each summary entry
        summaries = [remove_keys(summary, self.exclude_fields) for summary in summaries]

        if enable_course_filters:
            # Add list of associated program IDs to each summary entry
            programs_presenter = ProgramsPresenter(analytics_client=self.analytics_client)
            programs = programs_presenter.get_programs(course_ids=courses)
            for summary in summaries:
                summary_programs = [program for program in programs if summary['course_id'] in program['course_ids']]
                summary['program_ids'] = ' | '.join([program['program_id'] for program in summary_programs])
                summary['program_titles'] = ' | '.join([program['program_title'] for program in summary_programs])

        summaries_csv = self.renderer.render(summaries)
        return summaries_csv
