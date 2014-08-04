from django.core.urlresolvers import reverse
from waffle import switch_is_active


def _is_navbar_item_enabled(item):
    switch_name = item.get('switch', None)
    if switch_name:
        return switch_is_active(switch_name)
    return True


def navbar(request):
    """ Returns an array of dicts representing the items on the navigation bar. """

    course_id = request.course_id

    items = [
        {'title': 'Overview', 'href': reverse('courses:overview', kwargs={'course_id': course_id}),
         'icon': 'fa-tachometer', 'label': 'Overview', 'switch': 'navbar_display_overview'},
        {'title': 'Enrollment', 'href': reverse('courses:enrollment', kwargs={'course_id': course_id}),
         'icon': 'fa-child', 'label': 'Enrollment', 'switch': None},
        {'title': 'Engagement', 'href': reverse('courses:engagement', kwargs={'course_id': course_id}),
         'icon': 'fa-tasks', 'label': 'Engagement', 'switch': 'navbar_display_engagement'},
        {'title': None, 'href': '#', 'icon': 'fa-life-ring', 'label': 'Help & Support', 'switch': None},
        {'title': None, 'href': '#', 'icon': 'fa-comments-o', 'label': 'Contact', 'switch': None}
    ]

    items = filter(_is_navbar_item_enabled, items)

    return {'navbar_items': items}
