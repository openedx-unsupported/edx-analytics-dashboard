"""
This module contains various configuration settings via
waffle switches for edx's video abstraction layer.
"""


from edx_toggles.toggles import WaffleFlag

WAFFLE_NAMESPACE = 'analytics_dashboard'


def waffle_name(toggle_name):
    """
    Method to append waffle namespace to toggle's name

    Reason behind not using f-strings is backwards compatibility
    Since this is a method, it should be easy to change later on
    """
    return "{namespace}.{toggle_name}".format(
        namespace=WAFFLE_NAMESPACE,
        toggle_name=toggle_name,
    )


# .. toggle_name: IGNORE_ACCEPT_LANGUAGE
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Removes the Accept-Language header from incoming requests so that Django's
#   i18n machinery ignores it. While Accept-Language is the standard way of determining which language a user
#   should see, in practice too few users configure their browser away from the default of English, which can be
#   problematic for installations primarily geared toward audiences that speak other languages. Enabling this
#   setting makes the LANGUAGE_CODE Django setting the default language users will see when first visiting.
# .. toggle_use_cases: opt_in
# .. toggle_creation_date: 2021-01-15
# .. toggle_tickets: https://openedx.atlassian.net/browse/OSPR-5367
IGNORE_ACCEPT_LANGUAGE = WaffleFlag(
    waffle_name('ignore_accept_language'),
    module_name=__name__,
)
