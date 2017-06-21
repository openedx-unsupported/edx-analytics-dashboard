import copy
import logging

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _, ugettext_noop
from slugify import slugify
from waffle import switch_is_active

from core.utils import translate_dict_values
from courses.presenters.performance import CoursePerformancePresenter, TagsDistributionPresenter

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

    secondary_nav_items_base = [
        {
            'name': 'graded_content',
            'text': ugettext_noop('Graded Content'),
            'view': 'courses:performance:graded_content',
            'scope': 'course',
            'lens': 'performance',
            'report': 'graded',
            'depth': ''
        },
        {
            'name': 'ungraded_content',
            'text': ugettext_noop('Ungraded Problems'),
            'view': 'courses:performance:ungraded_content',
            'scope': 'course',
            'lens': 'performance',
            'report': 'ungraded',
            'depth': ''
        },
    ]
    translate_dict_values(secondary_nav_items_base, ('text',))
    secondary_nav_items = None
    active_primary_nav_item = 'performance'

    def get_context_data(self, **kwargs):
        self.secondary_nav_items = copy.deepcopy(self.secondary_nav_items_base)
        if switch_is_active('enable_performance_learning_outcome'):
            if not any(d['name'] == 'learning_outcomes' for d in self.secondary_nav_items):
                self.secondary_nav_items.append({
                    'name': 'learning_outcomes',
                    'text': ugettext_noop('Learning Outcomes'),
                    'view': 'courses:performance:learning_outcomes',
                    'scope': 'course',
                    'lens': 'performance',
                    'report': 'outcomes',
                    'depth': ''
                })
                translate_dict_values(self.secondary_nav_items, ('text',))

        context_data = super(PerformanceTemplateView, self).get_context_data(**kwargs)
        self.presenter = CoursePerformancePresenter(self.access_token, self.course_id)

        context_data['no_data_message'] = self.no_data_message
        context_data['js_data']['course'].update({
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
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'graded',
        'depth': 'problem'
    }


class PerformanceGradedContent(PerformanceGradedContentTemplateView):
    template_name = 'courses/performance_graded_content.html'
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'graded',
        'depth': ''
    }

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
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'graded',
        'depth': 'section'
    }

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
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'graded',
        'depth': 'subsection'
    }

    def get_context_data(self, **kwargs):
        context = super(PerformanceAssignment, self).get_context_data(**kwargs)

        context['js_data']['course'].update({
            'contentTableHeading': _('Problem Name'),
            'primaryContent': self.assignment['children']
        })

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context


class PerformanceUngradedContent(PerformanceUngradedContentTemplateView):
    template_name = 'courses/performance_ungraded_content.html'
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'ungraded',
        'depth': ''
    }

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
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'ungraded',
        'depth': 'section'
    }

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
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'ungraded',
        'depth': 'subsection'
    }

    def get_context_data(self, **kwargs):
        context = super(PerformanceUngradedSubsection, self).get_context_data(**kwargs)

        problems = self.presenter.subsection_children(self.section_id, self.subsection_id)
        self.set_primary_content(context, problems)
        context['js_data']['course']['contentTableHeading'] = _('Problem Name')

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context


class PerformanceUngradedAnswerDistribution(PerformanceAnswerDistributionMixin,
                                            PerformanceUngradedContentTemplateView):
    template_name = 'courses/performance_ungraded_answer_distribution.html'
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'ungraded',
        'depth': 'problem'
    }
    page_title = _('Performance: Problem Submissions')


class PerformanceLearningOutcomesMixin(PerformanceTemplateView):
    active_secondary_nav_item = 'learning_outcomes'
    tags_presenter = None
    selected_tag_value = None
    update_message = _('Tags distribution data was last updated %(update_date)s at %(update_time)s UTC.')
    no_data_message = _('No submissions received for these exercises.')

    def get_context_data(self, **kwargs):
        context = super(PerformanceLearningOutcomesMixin, self).get_context_data(**kwargs)

        self.selected_tag_value = kwargs.get('tag_value', None)
        self.tags_presenter = TagsDistributionPresenter(self.access_token, self.course_id)

        first_level_content_nav, first_selected_item = self.tags_presenter.get_tags_content_nav(
            'learning_outcome', self.selected_tag_value)

        context['selected_tag_value'] = self.selected_tag_value
        context['update_message'] = self.get_last_updated_message(self.tags_presenter.last_updated)
        context['js_data'] = {
            'first_level_content_nav': first_level_content_nav,
            'first_level_selected': first_selected_item
        }
        return context


class PerformanceLearningOutcomesContent(PerformanceLearningOutcomesMixin):
    template_name = 'courses/performance_learning_outcomes_content.html'
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'outcomes',
        'depth': ''
    }
    page_title = _('Performance: Learning Outcomes')

    def get_context_data(self, **kwargs):
        context = super(PerformanceLearningOutcomesContent, self).get_context_data(**kwargs)

        tags_distribution = self.tags_presenter.get_tags_distribution('learning_outcome')

        course_data = {'tagsDistribution': tags_distribution,
                       'hasData': bool(tags_distribution),
                       'courseId': self.course_id,
                       'contentTableHeading': "Outcome Name"}

        context['js_data'].update({
            'course': course_data,
        })
        context.update({
            'page_data': self.get_page_data(context),
        })

        return context


class PerformanceLearningOutcomesSection(PerformanceLearningOutcomesMixin):
    template_name = 'courses/performance_learning_outcomes_section.html'
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'outcomes',
        'depth': 'section'
    }
    page_title = _('Performance: Learning Outcomes')
    has_part_id_param = False

    def get_context_data(self, **kwargs):
        context = super(PerformanceLearningOutcomesSection, self).get_context_data(**kwargs)

        if self.has_part_id_param and self.part_id is None and self.problem_id:
            assignments = self.presenter.course_module_data()
            if self.problem_id in assignments and assignments[self.problem_id]['part_ids']:
                self.part_id = assignments[self.problem_id]['part_ids'][0]

        modules_marked_with_tag = self.tags_presenter.get_modules_marked_with_tag('learning_outcome',
                                                                                  self.selected_tag_value)
        course_data = {'tagsDistribution': modules_marked_with_tag,
                       'hasData': bool(modules_marked_with_tag),
                       'courseId': self.course_id,
                       'contentTableHeading': "Problem Name"}

        context['js_data'].update({
            'course': course_data,
            'second_level_content_nav': modules_marked_with_tag
        })
        context.update({
            'page_data': self.get_page_data(context),
        })

        return context


class PerformanceLearningOutcomesAnswersDistribution(PerformanceAnswerDistributionMixin,
                                                     PerformanceLearningOutcomesSection):
    template_name = 'courses/performance_learning_outcomes_answer_distribution.html'
    page_title = _('Performance: Problem Submissions')
    page_name = {
        'scope': 'course',
        'lens': 'performance',
        'report': 'outcomes',
        'depth': 'problem'
    }
    has_part_id_param = True

    def get_context_data(self, **kwargs):
        context = super(PerformanceLearningOutcomesAnswersDistribution, self).get_context_data(**kwargs)

        second_level_selected_item = None
        for nav_item in context['js_data']['second_level_content_nav']:
            if nav_item['id'] == self.problem_id:
                second_level_selected_item = nav_item
                break

        context['js_data'].update({
            'second_level_selected': second_level_selected_item
        })

        return context
