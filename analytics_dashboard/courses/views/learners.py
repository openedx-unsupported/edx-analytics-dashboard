import logging
from requests.exceptions import ConnectionError, Timeout

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from core.utils import feature_flagged
from courses.views import CourseTemplateWithNavView
from learner_analytics_api.v0.clients import LearnerAPIClient


logger = logging.getLogger(__name__)


@feature_flagged('enable_learner_analytics')
class LearnersView(CourseTemplateWithNavView):
    template_name = 'courses/learners.html'
    active_primary_nav_item = 'learners'
    page_title = _('Learners')
    page_name = 'learners'

    def get_context_data(self, **kwargs):
        context = super(LearnersView, self).get_context_data(**kwargs)
        context.update({
            'page_data': self.get_page_data(context),
            'learner_list_url': reverse('learner_analytics_api:v0:LearnerList'),
            'course_learner_metadata_url': reverse(
                'learner_analytics_api:v0:CourseMetadata',
                args=(self.course_id,)
            ),
        })
        # Try to prefetch API responses.  If anything fails, the front-end will
        # retry the requests and gracefully fail.
        client = LearnerAPIClient()
        for data_name, request_function, error_message in [
                (
                    'learner_list_json',
                    # TODO: https://openedx.atlassian.net/browse/AN-6841
                    lambda: client.learners.get(course_id=self.course_id).json(),
                    'Failed to reach the Learner List endpoint',
                ),
                (
                    'course_learner_metadata_json',
                    # TODO: https://openedx.atlassian.net/browse/AN-6841
                    lambda: client.course_learner_metadata(self.course_id).get().json(),
                    'Failed to reach the Course Learner Metadata endpoint',
                )
        ]:
            try:
                context[data_name] = request_function()
            except (Timeout, ConnectionError):
                logger.exception(error_message)
                context[data_name] = {}

        return context
