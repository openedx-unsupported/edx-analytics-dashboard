import logging

from django.utils.translation import ugettext_lazy as _

from analyticsclient.exceptions import NotFoundError

from courses.presenters.engagement import CourseEngagementPresenter
from courses.views import CourseTemplateWithNavView


logger = logging.getLogger(__name__)


class EngagementTemplateView(CourseTemplateWithNavView):
    """
    Base view for course engagement pages.
    """
    secondary_nav_items = [
        # Translators: Content as in course content (e.g. things, not the feeling)
        {'name': 'content', 'label': _('Content'), 'view': 'courses:engagement:content'},
    ]
    active_primary_nav_item = 'engagement'


class EngagementContentView(EngagementTemplateView):
    template_name = 'courses/engagement_content.html'
    page_title = _('Engagement Content')
    page_name = 'engagement_content'
    active_secondary_nav_item = 'content'

    # Translators: Do not translate UTC.
    update_message = _('Course engagement data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super(EngagementContentView, self).get_context_data(**kwargs)

        presenter = CourseEngagementPresenter(self.course_id)

        summary = None
        trends = None
        last_updated = None
        try:
            summary, trends = presenter.get_summary_and_trend_data()
            last_updated = summary['last_updated']
        except NotFoundError:
            logger.error("Failed to retrieve engagement content data for %s.", self.course_id)

        context['js_data']['course']['engagementTrends'] = trends
        context.update({
            'summary': summary,
            'update_message': self.get_last_updated_message(last_updated)
        })
        context['page_data'] = self.get_page_data(context)

        return context
