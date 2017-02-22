import logging

from braces.views import LoginRequiredMixin

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from waffle import switch_is_active

from courses import permissions
from courses.views import (
    CourseAPIMixin,
    LastUpdatedView,
    LazyEncoderMixin,
    TemplateView,
    TrackedViewMixin,
)
from courses.views.csv import CSVResponseMixin
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
            'enable_course_filters': switch_is_active('enable_course_filters')
        }
        context['js_data']['course'] = data
        context['page_data'] = self.get_page_data(context)
        return context


class CourseIndexCSV(CourseAPIMixin, LoginRequiredMixin, CSVResponseMixin, TemplateView):

    csv_filename_suffix = 'course-list'

    def _get_filename(self):
        """
        Returns the filename for the CSV download.
        """
        now = timezone.now().replace(microsecond=0)
        return u'{0}--{1}.csv'.format(now.isoformat(), self.csv_filename_suffix)

    def collapse_nested_dict(self, nested_dict, dot_separated_key):
        """Recursively flatten dictionary to a list of tuples with dot-separated keys and only atomic values.

        For example:
        self.collapse_nested_dict({
            'audit': {
                'count': 5,
                'count_change_7_days': 1,
                ...
            },
            'credit': {
                'count': 10,
                ...
            },
            ...
        }, ['enrollment_modes'])

        Should return:
        [
            ('enrollment_modes.audit.count', 5),
            ('enrollment_modes.audit.count_change_7_days', 1),
            ...
            ('enrollment_modes.credit.count', 10),
            ...
        ]
        """
        nested_key_val_pairs = []
        for key, val in nested_dict.items():
            if isinstance(val, dict):
                nested_key_val_pairs.extend(self.collapse_nested_dict(val, dot_separated_key + [key]))
            else:
                nested_key_val_pairs.append(('.'.join(dot_separated_key + [key]), val))
        return nested_key_val_pairs

    def convert_to_csv(self, summaries):
        # Convert the list of summaries dicts into a list of two-element lists where the first element is the column
        # header title and the second element is the value for the specified course.
        summaries_csv = []
        for i, summary in enumerate(summaries):
            summary_csv = []
            for key, val in summary.items():
                if isinstance(val, dict):
                    # Flatten nested dicts to a list of dot-separated keys and atomic values and add them to
                    # summary_csv
                    for nested_key, nested_val in self.collapse_nested_dict(val, [key]):
                        summary_csv.append([nested_key, nested_val])
                else:
                    summary_csv.append([key, val])
            # Since python dicts are unordered and we need deterministic output, sort summary_csv by the titles.
            summary_csv = sorted(summary_csv, key=lambda x: x[0])
            # Convert the list of columns into a string: the expected CSV response
            if i == 0:  # if this is the first row, also include the header
                summaries_csv.extend([','.join(unicode(col[i]) for col in summary_csv)
                                      for i in range(len(summary_csv[0]))])
            else:
                summaries_csv.append(','.join([unicode(col[1]) for col in summary_csv]))

        return '\n'.join(summaries_csv)

    def get_data(self):
        courses = permissions.get_user_course_permissions(self.request.user)
        if not courses:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        presenter = CourseSummariesPresenter()
        summaries, _ = presenter.get_course_summaries(courses)
        summaries_csv = self.convert_to_csv(summaries)
        return summaries_csv
