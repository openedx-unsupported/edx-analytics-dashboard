import ConfigParser
import logging

from django.conf import settings


log = logging.getLogger(__name__)


def _get_config_value_with_default(section_name, option, default_option="default"):
    """
    Args:
        section_name: name of the section in the configuration from which the option should be found
        option: name of the configuration option
        default_option: name of the default configuration option whose value should be returned if the
            requested option is not found
    """
    try:
        return settings.DOCS_CONFIG.get(section_name, option)
    except (ConfigParser.NoOptionError, AttributeError):
        log.debug("Didn't find a configuration option for '%s' section and '%s' option", section_name, option)
        return settings.DOCS_CONFIG.get(section_name, default_option)


def get_doc_url(page_token=None):
    """
    Returns:
        The URL for the documentation
    """
    return "{url_base}/{language}/{version}/{page_path}".format(
        url_base=settings.DOCS_CONFIG.get("help_settings", "url_base"),
        language=_get_config_value_with_default("locales", settings.LANGUAGE_CODE),
        version=settings.DOCS_CONFIG.get("help_settings", "version"),
        page_path=_get_config_value_with_default("pages", page_token),
    )
