import re

from django.apps import AppConfig
from django.conf import settings


class AnalyticsDashboardConfig(AppConfig):
    name = 'analytics_dashboard'
    verbose_name = 'Analytics Dashboard'

    def ready(self):
        super(AnalyticsDashboardConfig, self).ready()

        self._compile_segment_ignore_email_regex()

    def _compile_segment_ignore_email_regex(self):
        """ Compile and update the SEGMENT_IGNORE_EMAIL_REGEX setting. """
        if settings.SEGMENT_IGNORE_EMAIL_REGEX:
            settings.SEGMENT_IGNORE_EMAIL_REGEX = re.compile(settings.SEGMENT_IGNORE_EMAIL_REGEX, re.IGNORECASE)
