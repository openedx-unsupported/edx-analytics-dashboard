from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from courses.views import CourseNavBarMixin


class SingleUserNavbarMixin(CourseNavBarMixin):
    username = None

    def get_primary_nav_items(self):
        """
        Return the primary nav items.
        """

        items = [
            {'name': 'profile', 'label': _('User Profile'), 'view': 'courses:users:profile'},
            {'name': 'problems', 'label': _('Problem Data'), 'view': 'courses:users:problems'},
        ]

        # Clean each item
        map(self.clean_item, items)

        return items

    def clean_item(self, item):
        """
        Remove extraneous keys from item and set the href value.
        """
        # Prevent page reload if user clicks on the active navbar item, otherwise navigate to the new page.
        if item.get('active', False):
            href = '#'
        else:
            href = reverse(item['view'], kwargs={'course_id': self.course_id, 'username': self.username})

        item['href'] = href

        # Delete entries that are no longer needed
        item.pop('view', None)

    def dispatch(self, request, *args, **kwargs):
        self.username = kwargs.get('username')
        return super(SingleUserNavbarMixin, self).dispatch(request, *args, **kwargs)
