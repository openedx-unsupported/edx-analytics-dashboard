import logging

from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from analyticsclient.exceptions import NotFoundError

from courses.presenters.performance import CoursePerformancePresenter
from courses.views import CourseTemplateWithNavView


logger = logging.getLogger(__name__)


class PerformanceTemplateView(CourseTemplateWithNavView):
    # Translators: Do not translate UTC.
    update_message = _('Problem submission data was last updated %(update_date)s at %(update_time)s UTC.')


class PerformanceAnswerDistributionView(PerformanceTemplateView):
    template_name = 'courses/performance_answer_distribution.html'
    page_title = _('Performance: Problem Submissions')
    page_name = 'performance_answer_distribution'

    def get_context_data(self, **kwargs):
        context = super(PerformanceAnswerDistributionView, self).get_context_data(**kwargs)
        presenter = CoursePerformancePresenter(self.course_id)

        problem_id = self.kwargs['content_id']
        part_id = self.kwargs['problem_part_id']
        view_live_url = None

        if settings.LMS_COURSE_SHORTCUT_BASE_URL:
            view_live_url = '{0}/{1}/jump_to/{2}'.format(settings.LMS_COURSE_SHORTCUT_BASE_URL,
                                                         self.course_id, problem_id)

        try:
            answer_distribution_entry = presenter.get_answer_distribution(problem_id, part_id)
        except NotFoundError:
            logger.error("Failed to retrieve performance answer distribution data for %s.", part_id)
            # if the problem_part_id isn't found, a NotFoundError is thrown and a 404 should be displayed
            raise NotFoundError

        context['js_data']['course'].update({
            'answerDistribution': answer_distribution_entry.answer_distribution,
            'answerDistributionLimited': answer_distribution_entry.answer_distribution_limited,
            'isRandom': answer_distribution_entry.is_random,
            'answerType': answer_distribution_entry.answer_type
        })

        context.update({
            'course_id': self.course_id,
            'questions': answer_distribution_entry.questions,
            'active_question': answer_distribution_entry.active_question,
            'problem_id': problem_id,
            'problem_part_id': part_id,
            'problem_part_description': answer_distribution_entry.problem_part_description,
            'view_live_url': view_live_url,
            'update_message': self.get_last_updated_message(answer_distribution_entry.last_updated)
        })
        context['page_data'] = self.get_page_data(context)

        return context
