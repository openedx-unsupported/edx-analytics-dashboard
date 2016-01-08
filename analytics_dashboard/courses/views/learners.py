from django.utils.translation import ugettext_lazy as _

from courses.views import CourseTemplateWithNavView


class LearnersView(CourseTemplateWithNavView):
    template_name = 'courses/learners.html'
    active_primary_nav_item = 'learners'
    page_title = _('Learners')

    def get_context_data(self, **kwargs):
        context = super(LearnersView, self).get_context_data(**kwargs)
        context['page_data'] = self.get_page_data(context)
        return context
