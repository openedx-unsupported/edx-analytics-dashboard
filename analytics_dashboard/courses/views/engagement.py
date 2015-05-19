import logging

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from analyticsclient.exceptions import NotFoundError

from courses.presenters.engagement import (CourseEngagementActivityPresenter, CourseEngagementVideoPresenter)
from courses.views import (CourseStructureMixin, CourseStructureExceptionMixin, CourseTemplateWithNavView)


logger = logging.getLogger(__name__)


class EngagementTemplateView(CourseTemplateWithNavView):
    """
    Base view for course engagement pages.
    """
    secondary_nav_items = [
        # Translators: Content as in course content (e.g. things, not the feeling)
        {'name': 'content', 'label': _('Content'), 'view': 'courses:engagement:content'},
        {'name': 'videos', 'label': _('Videos'), 'view': 'courses:engagement:videos', 'switch': 'enable_course_api'},
    ]
    active_primary_nav_item = 'engagement'
    presenter = None


class EngagementContentView(EngagementTemplateView):
    template_name = 'courses/engagement_content.html'
    page_title = _('Engagement Content')
    page_name = 'engagement_content'
    active_secondary_nav_item = 'content'

    # Translators: Do not translate UTC.
    update_message = _('Course engagement data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super(EngagementContentView, self).get_context_data(**kwargs)
        self.presenter = CourseEngagementActivityPresenter(self.course_id)

        summary = None
        trends = None
        last_updated = None
        try:
            summary, trends = self.presenter.get_summary_and_trend_data()
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


class EngagementVideoContentTemplateView(CourseStructureMixin, CourseStructureExceptionMixin, EngagementTemplateView):
    page_title = _('Engagement Videos')
    active_secondary_nav_item = 'videos'
    section_id = None
    subsection_id = None
    # Translators: Do not translate UTC.
    update_message = _('Video data was last updated %(update_date)s at %(update_time)s UTC.')
    no_data_message = _('Looks like no one has watched any videos in these sections.')

    def get_context_data(self, **kwargs):
        self.presenter = CourseEngagementVideoPresenter(self.access_token, self.course_id)
        context = super(EngagementVideoContentTemplateView, self).get_context_data(**kwargs)
        context['js_data']['course'].update({
            'showVideoCount': True,  # overwrite to hide video count column
        })
        context.update({
            'sections': self.presenter.sections(),
            'update_message': self.get_last_updated_message(self.presenter.last_updated),
            'no_data_message': self.no_data_message
        })

        return context


class EngagementVideoCourse(EngagementVideoContentTemplateView):
    template_name = 'courses/engagement_video_course.html'
    page_name = 'engagement_videos'

    def get_context_data(self, **kwargs):
        context = super(EngagementVideoCourse, self).get_context_data(**kwargs)
        self.set_primary_content(context, self.presenter.sections())
        context['js_data']['course']['contentTableHeading'] = _('Section Name')
        context.update({
            'page_data': self.get_page_data(context)
        })
        return context


class EngagementVideoSection(EngagementVideoContentTemplateView):
    template_name = 'courses/engagement_video_by_section.html'
    page_name = 'engagement_videos'

    def get_context_data(self, **kwargs):
        context = super(EngagementVideoSection, self).get_context_data(**kwargs)
        sub_sections = self.presenter.subsections(self.section_id)
        self.set_primary_content(context, sub_sections)
        context['js_data']['course']['contentTableHeading'] = _('Subsection Name')
        context.update({
            'page_data': self.get_page_data(context)
        })
        return context


class EngagementVideoSubsection(EngagementVideoContentTemplateView):
    template_name = 'courses/engagement_video_by_subsection.html'
    page_name = 'engagement_videos'

    def get_context_data(self, **kwargs):
        context = super(EngagementVideoSubsection, self).get_context_data(**kwargs)
        videos = self.presenter.subsection_children(self.section_id, self.subsection_id)
        self.set_primary_content(context, videos)
        context['js_data']['course'].update({
            'contentTableHeading': _('Video Name'),
            'showVideoCount': False,  # overwrite to hide video count column
        })
        context.update({
            'page_data': self.get_page_data(context)
        })
        return context


class EngagementVideoTimeline(EngagementVideoContentTemplateView):
    template_name = 'courses/engagement_video_timeline.html'
    page_name = 'engagement_videos'
    video_id = None

    def dispatch(self, request, *args, **kwargs):
        self.video_id = kwargs.get('video_id', None)
        return super(EngagementVideoTimeline, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EngagementVideoTimeline, self).get_context_data(**kwargs)

        video_data_id = self.presenter.module_id_to_data_id({'id': self.video_id})
        video_module = self.presenter.subsection_child(self.section_id, self.subsection_id, video_data_id)
        if video_module:
            timeline = self.presenter.get_video_timeline(video_module)

            videos = self.presenter.subsection_children(self.section_id, self.subsection_id)
            self.set_primary_content(context, videos)
            context.update({
                'video': self.presenter.block(self.video_id),
                'summary_metrics': video_module,
                'view_live_url': self.presenter.build_view_live_url(settings.LMS_COURSE_SHORTCUT_BASE_URL,
                                                                    self.video_id),
                'page_data': self.get_page_data(context)
            })

            context['js_data']['course'].update({
                'videoTimeline': timeline,
            })
            context.update({
                'page_data': self.get_page_data(context)
            })
        else:
            raise Http404

        return context
