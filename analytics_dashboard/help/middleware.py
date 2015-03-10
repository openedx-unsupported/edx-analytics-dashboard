from help import HELP_CONTEXT_TOKEN_NAME
from help.utils import get_doc_url


class HelpURLMiddleware(object):
    """
    Adds a "help_url" entry to the response context.
    """

    def process_template_response(self, _request, response):
        # Error responses do not have context.
        if response.status_code in [500, 503]:
            return response

        page_token = response.context_data.get(HELP_CONTEXT_TOKEN_NAME)
        response.context_data['help_url'] = get_doc_url(page_token)
        return response
