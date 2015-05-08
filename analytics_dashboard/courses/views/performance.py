import logging

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from slugify import slugify

from courses.presenters.performance import CoursePerformancePresenter
from courses.views import (
    CourseTemplateWithNavView,
    CourseAPIMixin,
    CourseStructureMixin,
    CourseStructureExceptionMixin)


logger = logging.getLogger(__name__)


class PerformanceTemplateView(CourseStructureExceptionMixin, CourseTemplateWithNavView, CourseAPIMixin):
    """
    Base view for course performance pages.
    """
    presenter = None
    problem_id = None
    part_id = None
    no_data_message = None

    # Translators: Do not translate UTC.
    update_message = _('Problem submission data was last updated %(update_date)s at %(update_time)s UTC.')

    secondary_nav_items = [
        {'name': 'graded_content', 'label': _('Graded Content'), 'view': 'courses:performance:graded_content'},
        {'name': 'ungraded_content', 'label': _('Ungraded Problems'), 'view': 'courses:performance:ungraded_content'}
    ]

    active_primary_nav_item = 'performance'

    def get_context_data(self, **kwargs):
        context_data = super(PerformanceTemplateView, self).get_context_data(**kwargs)
        self.presenter = CoursePerformancePresenter(self.access_token, self.course_id)

        context_data['no_data_message'] = self.no_data_message
        context_data['js_data']['course'].update({
            'showProblemCount': True,  # overwrite to hide problem count column
            'contentTableHeading': _('Assignment Name')  # overwrite for different heading
        })

        return context_data


class PerformanceUngradedContentTemplateView(CourseStructureMixin, PerformanceTemplateView):
    page_title = _('Ungraded Problems')
    active_secondary_nav_item = 'ungraded_content'
    section_id = None
    subsection_id = None
    no_data_message = _('No submissions received for these exercises.')

    def get_context_data(self, **kwargs):
        context = super(PerformanceUngradedContentTemplateView, self).get_context_data(**kwargs)
        context.update({
            'update_message': self.get_last_updated_message(self.presenter.last_updated)
        })
        return context


class PerformanceGradedContentTemplateView(PerformanceTemplateView):
    page_title = _('Graded Content')
    active_secondary_nav_item = 'graded_content'
    assignment_type = None
    assignment_id = None
    assignment = None
    no_data_message = _('No submissions received for these assignments.')

    def dispatch(self, request, *args, **kwargs):
        self.assignment_id = kwargs.get('assignment_id')
        return super(PerformanceGradedContentTemplateView, self).dispatch(request, *args, **kwargs)

    def _deslugify_assignment_type(self):
        """
        Assignment type is slugified in the templates to avoid issues with our URL regex failing to match unknown
        assignment types. This method changes the assignment type to the human-friendly version. If no match is found,
        the assignment type is unchanged.
        """
        for assignment_type in self.presenter.assignment_types():
            if self.assignment_type['name'] == slugify(assignment_type['name']):
                self.assignment_type = assignment_type
                break

    def get_context_data(self, **kwargs):
        context = super(PerformanceGradedContentTemplateView, self).get_context_data(**kwargs)
        context['assignment_types'] = self.presenter.assignment_types()

        if self.assignment_id:
            assignment = self.presenter.assignment(self.assignment_id)
            if assignment:
                context['assignment'] = assignment
                self.assignment = assignment
                self.assignment_type = {'name': assignment['assignment_type']}
            else:
                logger.info('Assignment %s not found.', self.assignment_id)
                raise Http404

        if self.assignment_type:
            self._deslugify_assignment_type()
            assignments = self.presenter.assignments(self.assignment_type)

            context['js_data']['course']['assignments'] = assignments
            context['js_data']['course']['hasData'] = self.presenter.blocks_have_data(assignments)
            context['js_data']['course']['assignmentType'] = self.assignment_type

            context.update({
                'assignment_type': self.assignment_type,
                'assignments': assignments,
                'update_message': self.get_last_updated_message(self.presenter.last_updated)
            })

        return context


class PerformanceAnswerDistributionMixin(object):
    presenter = None
    course_id = None
    problem_id = None
    part_id = None

    def dispatch(self, request, *args, **kwargs):
        self.problem_id = kwargs.get('problem_id', None)
        self.part_id = kwargs.get('problem_part_id', None)
        return super(PerformanceAnswerDistributionMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PerformanceAnswerDistributionMixin, self).get_context_data(**kwargs)

        answer_distribution_entry = self.presenter.get_answer_distribution(self.problem_id, self.part_id)

        context['js_data']['course'].update({
            'answerDistribution': answer_distribution_entry.answer_distribution,
            'answerDistributionLimited': answer_distribution_entry.answer_distribution_limited,
            'isRandom': answer_distribution_entry.is_random,
            'answerType': answer_distribution_entry.answer_type
        })

        context.update({
            'problem': self.presenter.block(self.problem_id),
            'questions': answer_distribution_entry.questions,
            'active_question': answer_distribution_entry.active_question,
            'problem_id': self.problem_id,
            'problem_part_id': self.part_id,
            'problem_part_description': answer_distribution_entry.problem_part_description,
            'view_live_url': self.presenter.build_view_live_url(settings.LMS_COURSE_SHORTCUT_BASE_URL, self.problem_id),
        })

        context['page_data'] = self.get_page_data(context)

        return context


class PerformanceAnswerDistributionView(PerformanceAnswerDistributionMixin,
                                        PerformanceGradedContentTemplateView):
    template_name = 'courses/performance_answer_distribution.html'
    page_title = _('Performance: Problem Submissions')
    page_name = 'performance_answer_distribution'


class PerformanceGradedContent(PerformanceGradedContentTemplateView):
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


class PerformanceGradedContentByType(PerformanceGradedContentTemplateView):
    template_name = 'courses/performance_graded_content_by_type.html'
    page_name = 'performance_graded_content_by_type'

    def dispatch(self, request, *args, **kwargs):
        self.assignment_type = {'name': kwargs['assignment_type']}
        return super(PerformanceGradedContentByType, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PerformanceGradedContentByType, self).get_context_data(**kwargs)

        assignment_type = self.assignment_type
        assignments = self.presenter.assignments(assignment_type)

        if not assignments:
            # If there are no assignments, either the course is incomplete or the assignment type is invalid.
            # It is more likely that the assignment type is invalid, so return a 404.
            logger.info('No assignments of type %s were found for course %s', assignment_type['name'], self.course_id)

        context['js_data']['course'].update({
            'primaryContent': assignments
        })

        context.update({
            'page_data': self.get_page_data(context),
            'page_title': _('Graded Content: %(assignment_type)s') % {'assignment_type': self.assignment_type['name']}
        })

        return context


class PerformanceAssignment(PerformanceGradedContentTemplateView):
    template_name = 'courses/performance_assignment.html'
    page_name = 'performance_assignment'

    def get_context_data(self, **kwargs):
        context = super(PerformanceAssignment, self).get_context_data(**kwargs)

        context['js_data']['course'].update({
            'contentTableHeading': _('Problem Name'),
            'primaryContent': self.assignment['children'],
            'showProblemCount': False  # hide the problem count column
        })

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context


class PerformanceUngradedContent(PerformanceUngradedContentTemplateView):
    template_name = 'courses/performance_ungraded_content.html'
    page_name = 'performance_ungraded_content'

    def get_context_data(self, **kwargs):
        context = super(PerformanceUngradedContent, self).get_context_data(**kwargs)

        self.set_primary_content(context, self.presenter.sections())
        context['js_data']['course']['contentTableHeading'] = _('Section Name')
        context.update({
            'page_data': self.get_page_data(context),
        })

        return context


class PerformanceUngradedSection(PerformanceUngradedContentTemplateView):
    template_name = 'courses/performance_ungraded_by_section.html'
    page_name = 'performance_ungraded_by_section'

    def get_context_data(self, **kwargs):
        context = super(PerformanceUngradedSection, self).get_context_data(**kwargs)

        sub_sections = self.presenter.subsections(self.section_id)
        self.set_primary_content(context, sub_sections)
        context['js_data']['course']['contentTableHeading'] = _('Subsection Name')
        context.update({
            'page_data': self.get_page_data(context)
        })

        return context


class PerformanceUngradedSubsection(PerformanceUngradedContentTemplateView):
    template_name = 'courses/performance_ungraded_by_subsection.html'
    page_name = 'performance_ungraded_by_subsection'

    def get_context_data(self, **kwargs):
        context = super(PerformanceUngradedSubsection, self).get_context_data(**kwargs)

        problems = self.presenter.subsection_children(self.section_id, self.subsection_id)
        self.set_primary_content(context, problems)
        context['js_data']['course']['contentTableHeading'] = _('Problem Name')
        context['js_data']['course'].update({
            'showProblemCount': False  # hide the problem count column
        })

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context


class PerformanceUngradedAnswerDistribution(PerformanceAnswerDistributionMixin,
                                            PerformanceUngradedContentTemplateView):
    template_name = 'courses/performance_ungraded_answer_distribution.html'
    page_name = 'performance_ungraded_answer_distribution'
    page_title = _('Performance: Problem Submissions')
