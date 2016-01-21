from requests.exceptions import ConnectTimeout

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from courses.views import CourseTemplateWithNavView
from learner_analytics_api.v0.clients import LearnerAPIClient


class LearnersView(CourseTemplateWithNavView):
    template_name = 'courses/learners.html'
    active_primary_nav_item = 'learners'
    page_title = _('Learners')
    page_name = 'learners'

    def get_context_data(self, **kwargs):
        context = super(LearnersView, self).get_context_data(**kwargs)
        context.update({
            'page_data': self.get_page_data(context),
            'learner_list_url': reverse('learner_analytics_api:v0:LearnerList')
        })
        # Try to grab the first page of learners.  If the analytics
        # API times out, the front-end will attempt to asynchronously
        # fetch the first page.
        client = LearnerAPIClient()
        try:
            context['learner_list_json'] = client.learners.get(course_id=self.course_id).json()
        except ConnectTimeout:
            context['learner_list_json'] = None
        return context
