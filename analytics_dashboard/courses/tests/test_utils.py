from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from waffle.testutils import override_flag, override_switch

import courses.utils as utils


class UtilsTest(TestCase):
    def test_is_feature_enabled(self):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        # Return True if no switch or flag are provided
        self.assertTrue(utils.is_feature_enabled({'switch': None, 'flag': None}, request))

        name = 'test-waffle'
        item = {'switch': 'test-waffle'}
        # Return False if switch inactive
        with override_switch(name, active=False):
            self.assertFalse(utils.is_feature_enabled(item, request))

        # Return True if switch active
        with override_switch(name, active=True):
            self.assertTrue(utils.is_feature_enabled(item, request))

        item = {'flag': 'test-waffle'}
        # Return False if flag inactive
        with override_flag(name, active=False):
            self.assertFalse(utils.is_feature_enabled(item, request))

        # Return True if flag active
        with override_flag(name, active=True):
            self.assertTrue(utils.is_feature_enabled(item, request))


class NumberTests(TestCase):
    def test_is_number(self):
        self.assertTrue(utils.number.is_number('-123'))
        self.assertTrue(utils.number.is_number('12678.123'))
        self.assertFalse(utils.number.is_number('45Test'))
        self.assertFalse(utils.number.is_number('edx'))
