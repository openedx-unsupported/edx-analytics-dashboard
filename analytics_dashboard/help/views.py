from __future__ import absolute_import

from help import HELP_CONTEXT_TOKEN_NAME


class ContextSensitiveHelpMixin:
    """
    Adds page-specific data to enable context-sensitive help.
    """

    help_token = None

    def get_context_data(self, **kwargs):
        context = super(ContextSensitiveHelpMixin, self).get_context_data(**kwargs)
        context[HELP_CONTEXT_TOKEN_NAME] = self.help_token
        return context
