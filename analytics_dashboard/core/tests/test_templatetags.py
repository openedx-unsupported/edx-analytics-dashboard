#!/usr/bin/python


import json

from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase
from opaque_keys.edx.keys import CourseKey

from analytics_dashboard.core.templatetags import dashboard_extras
from analytics_dashboard.core.templatetags.dashboard_extras import format_course_key


class DashboardExtraTests(TestCase):
    def test_settings_value(self):
        template = Template(
            "{% load dashboard_extras %}"
            "{% settings_value \"FAKE_SETTING\" %}"
        )

        # If setting is not found, tag returns None.
        self.assertRaises(AttributeError, template.render, Context())

        with self.settings(FAKE_SETTING='edX'):
            # If setting is found, tag simply displays setting value.
            self.assertEqual(template.render(Context()), "edX")

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
                          "{% load dashboard_extras %}{% captureas %}42{%endcaptureas%}")

        self.assertTextCaptured('42')

    def test_captureas_unicode(self):
        self.assertTextCaptured('★❤')

    def test_format_course_key(self):
        values = [('edX/DemoX/Demo_Course', 'edX/DemoX/Demo_Course'),
                  ('course-v1:edX+DemoX+Demo_2014', 'edX/DemoX/Demo_2014'),
                  ('ccx-v1:edx+1.005x-CCX+rerun+ccx@15', 'edx/1.005x-CCX/rerun')]
        for course_id, expected in values:
            # Test with CourseKey
            course_key = CourseKey.from_string(course_id)
            self.assertEqual(format_course_key(course_key), expected)

            # Test with string
            self.assertEqual(format_course_key(course_id), expected)

    def test_metric_percentage(self):
        self.assertEqual(dashboard_extras.metric_percentage(0), '0%')
        self.assertEqual(dashboard_extras.metric_percentage(0.009), '< 1%')
        self.assertEqual(dashboard_extras.metric_percentage(0.5066), '50.7%')
        self.assertEqual(dashboard_extras.metric_percentage(0.5044), '50.4%')

    def test_unicode_slugify(self):
        self.assertEqual(dashboard_extras.unicode_slugify('hello world'), 'hello-world')
        self.assertEqual(dashboard_extras.unicode_slugify('straße road'), 'strasse-road')

    def test_escape_json(self):
        data_as_dict = {'user_bio': '</script><script>alert("&hellip;"!)</script>'}
        data_as_json = json.dumps(data_as_dict)
        expected_json = \
            '{"user_bio": "\\u003c/script\\u003e\\u003cscript\\u003ealert(\\"\\u0026hellip;\\"!)\\u003c/script\\u003e"}'
        self.assertEqual(dashboard_extras.escape_json(data_as_dict), expected_json)
        self.assertEqual(dashboard_extras.escape_json(data_as_json), expected_json)

    def test_languade_code_to_cldr(self):
        # standard cases
        self.assertEqual(dashboard_extras.languade_code_to_cldr('en'), 'en')
        self.assertEqual(dashboard_extras.languade_code_to_cldr('en-Us'), 'en-US')
        self.assertEqual(dashboard_extras.languade_code_to_cldr('en-gb'), 'en-GB')

        self.assertEqual(dashboard_extras.languade_code_to_cldr('az-latn'), 'az-Latn')
        self.assertEqual(dashboard_extras.languade_code_to_cldr('pa-guru'), 'pa-Guru')

        self.assertEqual(dashboard_extras.languade_code_to_cldr('sr-cyrl'), 'sr-Cyrl')
        self.assertEqual(dashboard_extras.languade_code_to_cldr('sr-cyrl-ba'), 'sr-Cyrl-BA')

        self.assertEqual(dashboard_extras.languade_code_to_cldr('ca-es-valencia'), 'ca-ES-VALENCIA')
        self.assertEqual(dashboard_extras.languade_code_to_cldr('en-us-posix'), 'en-US-POSIX')

        # traditional Chinese cases
        for language_code in ['zh-tw', 'zh-hk', 'zh-mo', 'zh-hant']:
            self.assertEqual(dashboard_extras.languade_code_to_cldr(language_code), 'zh-Hant')

        # simplified Chinese cases
        for language_code in ['zh-cn', 'zh-sg', 'zh-hans']:
            self.assertEqual(dashboard_extras.languade_code_to_cldr(language_code), 'zh')
