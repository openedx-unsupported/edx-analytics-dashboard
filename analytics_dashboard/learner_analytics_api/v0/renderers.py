"""
Custom Django REST Framework rendererers used by the learner analytics API views.
"""
from __future__ import absolute_import

from rest_framework.renderers import BaseRenderer


class TextRenderer(BaseRenderer):
    """Renders the REST response data without modification."""

    def render(self, data, *_args, **_kwargs):
        """Return the data unchanged."""
        return data
