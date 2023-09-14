import json

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from analytics_dashboard.courses.serializers import LazyEncoder


class CourseEngagementPresenterTests(TestCase):

    def test_lazy_encode(self):
        primary = _('Primary')
        expected = '{{"education_level": "{0}"}}'.format(str(primary))
        actual = json.dumps({'education_level': primary}, cls=LazyEncoder)
        self.assertEqual(actual, expected)
