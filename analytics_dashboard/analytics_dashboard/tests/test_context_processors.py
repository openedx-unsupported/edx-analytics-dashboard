from django.core.urlresolvers import reverse

from django.test import TestCase, RequestFactory
from django_dynamic_fixture import G
from waffle import Switch

from analytics_dashboard.context_processors import navbar


class NavbarContextProcessorTests(TestCase):
    def test_navbar(self):
        """
        Verify the navbar context processor returns the appropriate navbar items
        """
        course_id = 'edX/DemoX/Demo_Course'
        request = RequestFactory().get('/')
        request.course_id = course_id

        context = navbar(request)
        complete = [
            {'title': 'Overview', 'href': reverse('courses:overview', kwargs={'course_id': course_id}),
             'icon': 'fa-tachometer', 'label': 'Overview', 'switch': 'navbar_display_overview'},
            {'title': 'Enrollment', 'href': reverse('courses:enrollment', kwargs={'course_id': course_id}),
             'icon': 'fa-child', 'label': 'Enrollment', 'switch': None},
            {'title': 'Engagement', 'href': reverse('courses:engagement', kwargs={'course_id': course_id}),
             'icon': 'fa-tasks', 'label': 'Engagement', 'switch': 'navbar_display_engagement'},
            {'title': None, 'href': '#', 'icon': 'fa-life-ring', 'label': 'Help & Support', 'switch': None},
            {'title': None, 'href': '#', 'icon': 'fa-comments-o', 'label': 'Contact', 'switch': None}
        ]

        expected = [item for item in complete if not item['switch']]
        self.assertListEqual(context['navbar_items'], expected)

        # Verify feature switching enables items
        G(Switch, name='navbar_display_overview', active=True)
        G(Switch, name='navbar_display_engagement', active=True)
        context = navbar(request)
        self.assertListEqual(context['navbar_items'], complete)

    def test_without_course_id(self):
        request = RequestFactory().get('/')
        context = navbar(request)
        self.assertDictEqual(context, {})
