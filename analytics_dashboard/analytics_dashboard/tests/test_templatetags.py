from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase


class DashboardExtraTests(TestCase):
    def test_settings_value(self):
        template = Template(
            "{% load dashboard_extras %}"
            "{% settings_value \"FAKE_SETTING\" %}"
        )

        # If setting is not found, tag returns None.
        self.assertEqual(template.render(Context()), "None")

        with self.settings(FAKE_SETTING='edX'):
            # If setting is found, tag simply displays setting value.
            self.assertEqual(template.render(Context()), "edX")

    def test_captureas(self):
        # Tag requires a variable name.
        self.assertRaises(TemplateSyntaxError, Template,
                          "{% load dashboard_extras %}" "{% captureas %}42{%endcaptureas%}")

        template = Template(
            "{% load dashboard_extras %}"
            "{% captureas foo %}42{%endcaptureas%}"
            "{{ foo }}"
        )

        # Tag should render the value captured in the block.
        self.assertEqual(template.render(Context()), "42")
