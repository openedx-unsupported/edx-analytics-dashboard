from django.test import TestCase
from waffle import Switch

import courses.utils as utils


class UtilsTest(TestCase):
    def test_is_feature_enabled(self):
        name = 'test-switch'
        item = {'switch': name}

        # Return True if no switch provided
        self.assertTrue(utils.is_feature_enabled({'switch': None}))

        # Return False if switch inactive
        switch = Switch.objects.create(name=name, active=False)
        self.assertFalse(utils.is_feature_enabled(item))

        # Return True if switch active
        switch.active = True
        switch.save()
        self.assertTrue(utils.is_feature_enabled(item))
