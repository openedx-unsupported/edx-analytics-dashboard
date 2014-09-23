#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase


class DashboardExtraTests(TestCase):
    def assertTextCaptured(self, expected):
        template = Template(
            "{% load dashboard_extras %}"
            "{% captureas foo %}{{ expected }}{%endcaptureas%}"
            "{{ foo }}"
        )
        # Tag should render the value captured in the block.
        self.assertEqual(template.render(Context({'expected': expected})), expected)

    def test_captureas(self):
        # Tag requires a variable name.
        self.assertRaises(TemplateSyntaxError, Template,
                          "{% load dashboard_extras %}" "{% captureas %}42{%endcaptureas%}")

        self.assertTextCaptured('42')

    def test_captureas_unicode(self):
        self.assertTextCaptured(u'★❤')
