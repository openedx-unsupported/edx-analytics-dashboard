from __future__ import absolute_import

import json

import six
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from analytics_dashboard.courses.serializers import LazyEncoder


class CourseEngagementPresenterTests(TestCase):

    def test_lazy_encode(self):
        primary = _('Primary')
        expected = '{{"education_level": "{0}"}}'.format(six.text_type(primary))
        actual = json.dumps({'education_level': primary}, cls=LazyEncoder)
        self.assertEqual(actual, expected)
