import logging

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from slugify import slugify
from slumber.exceptions import SlumberBaseException

from courses.presenters.performance import CoursePerformancePresenter
from courses.views import CourseTemplateWithNavView, CourseAPIMixin


logger = logging.getLogger(__name__)


class PerformanceTemplateView(CourseTemplateWithNavView, CourseAPIMixin):
    """
    Base view for course performance pages.
    """
    assignment_type = None
    assignment_id = None
    assignment = None
    presenter = None

    # Translators: Do not translate UTC.
    update_message = _('Problem submission data was last updated %(update_date)s at %(update_time)s UTC.')

    secondary_nav_items = [
        {'name': 'graded_content', 'label': _('Graded Content'), 'view': 'courses:performance_graded_content'},
    ]
    active_primary_nav_item = 'performance'
    page_title = _('Graded Content')
    active_secondary_nav_item = 'graded_content'

    def dispatch(self, request, *args, **kwargs):
        self.assignment_id = kwargs.get('assignment_id')

        try:
            return super(PerformanceTemplateView, self).dispatch(request, *args, **kwargs)
        except SlumberBaseException as e:
            # Return the appropriate response if a 404 occurred.
            response = getattr(e, 'response')
            if response is not None and response.status_code == 404:
                logger.info('Course API data not found for %s: %s', self.course_id, e)
                raise Http404

            # Not a 404. Continue raising the error.
            logger.error('An error occurred while using Slumber to communicate with an API: %s', e)
            raise

    def _deslugify_assignment_type(self):
        """
        Assignment type is slugified in the templates to avoid issues with our URL regex failing to match unknown
        assignment types. This method changes the assignment type to the human-friendly version. If no match is found,
        the assignment type is unchanged.
        """
        for assignment_type in self.presenter.assignment_types():
            if self.assignment_type == slugify(assignment_type):
                self.assignment_type = assignment_type
                break

    def get_context_data(self, **kwargs):
        context = super(PerformanceTemplateView, self).get_context_data(**kwargs)
        self.presenter = CoursePerformancePresenter(self.access_token, self.course_id)

        context['assignment_types'] = self.presenter.assignment_types()

        if self.assignment_id:
            assignment = self.presenter.assignment(self.assignment_id)
            if assignment:
                context['assignment'] = assignment
                self.assignment = assignment
                self.assignment_type = assignment['assignment_type']
            else:
                logger.info('Assignment %s not found.', self.assignment_id)
                raise Http404

        if self.assignment_type:
            self._deslugify_assignment_type()
            assignments = self.presenter.assignments(self.assignment_type)

            context['js_data']['course']['assignments'] = assignments
            context['js_data']['course']['assignmentsHaveSubmissions'] = self.presenter.has_submissions(assignments)
            context['js_data']['course']['assignmentType'] = self.assignment_type

            context.update({
                'assignment_type': self.assignment_type,
                'assignments': assignments,
                'update_message': self.get_last_updated_message(self.presenter.last_updated)
            })

        return context


class PerformanceAnswerDistributionView(PerformanceTemplateView):
    template_name = 'courses/performance_answer_distribution.html'
    page_title = _('Performance: Problem Submissions')
    page_name = 'performance_answer_distribution'

    def get_context_data(self, **kwargs):
        context = super(PerformanceAnswerDistributionView, self).get_context_data(**kwargs)
        presenter = self.presenter

        problem_id = self.kwargs['problem_id']
        part_id = self.kwargs['problem_part_id']
        view_live_url = None

        if settings.LMS_COURSE_SHORTCUT_BASE_URL:
            view_live_url = u'{0}/{1}/jump_to/{2}'.format(settings.LMS_COURSE_SHORTCUT_BASE_URL, self.course_id,
                                                          problem_id)

        answer_distribution_entry = presenter.get_answer_distribution(problem_id, part_id)

        context['js_data']['course'].update({
            'answerDistribution': answer_distribution_entry.answer_distribution,
            'answerDistributionLimited': answer_distribution_entry.answer_distribution_limited,
            'isRandom': answer_distribution_entry.is_random,
            'answerType': answer_distribution_entry.answer_type
        })

        context.update({
            'problem': presenter.problem(problem_id),
            'questions': answer_distribution_entry.questions,
            'active_question': answer_distribution_entry.active_question,
            'problem_id': problem_id,
            'problem_part_id': part_id,
            'problem_part_description': answer_distribution_entry.problem_part_description,
            'view_live_url': view_live_url
        })

        context['page_data'] = self.get_page_data(context)

        return context


class PerformanceGradedContent(PerformanceTemplateView):
    template_name = 'courses/performance_graded_content.html'
    page_name = 'performance_graded_content'

    def get_context_data(self, **kwargs):
        context = super(PerformanceGradedContent, self).get_context_data(**kwargs)
        grading_policy = self.presenter.grading_policy()

        context.update({
            'grading_policy': grading_policy,
            'max_policy_display_percent': self.presenter.get_max_policy_display_percent(grading_policy),
            'min_policy_display_percent': CoursePerformancePresenter.MIN_POLICY_DISPLAY_PERCENT,
            'page_data': self.get_page_data(context)
        })

        return context


class PerformanceGradedContentByType(PerformanceTemplateView):
    template_name = 'courses/performance_graded_content_by_type.html'
    page_name = 'performance_graded_content_by_type'

    def dispatch(self, request, *args, **kwargs):
        self.assignment_type = kwargs['assignment_type']
        return super(PerformanceGradedContentByType, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PerformanceGradedContentByType, self).get_context_data(**kwargs)

        assignment_type = self.assignment_type
        assignments = self.presenter.assignments(assignment_type)

        if not assignments:
            # If there are no assignments, either the course is incomplete or the assignment type is invalid.
            # It is more likely that the assignment type is invalid, so return a 404.
            logger.info('No assignments of type %s were found for course %s', assignment_type, self.course_id)
            raise Http404

        context.update({
            'page_data': self.get_page_data(context),
            'page_title': _('Graded Content: %(assignment_type)s') % {'assignment_type': self.assignment_type}
        })

        return context


class PerformanceAssignment(PerformanceTemplateView):
    template_name = 'courses/performance_assignment.html'
    page_name = 'performance_assignment'

    def get_context_data(self, **kwargs):
        context = super(PerformanceAssignment, self).get_context_data(**kwargs)

        context['js_data']['course']['problems'] = self.assignment['problems']

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context
