"""
This module contains various configuration toggles
for edx's analytics dashboard.
"""


from edx_toggles.toggles import SettingToggle

# .. toggle_name: ENROLLMENT_AGE_AVAILABLE
# .. toggle_implementation: SettingToggle
# .. toggle_default: True
# .. toggle_description: Turn this toggle on to show age demographic information in the analytics dashboard.
#      Turn it off if your installation cannot or does not collect or share age information.
# .. toggle_use_cases: opt_out
# .. toggle_creation_date: 2021-01-12
# .. toggle_tickets: https://openedx.atlassian.net/browse/MST-1241
ENROLLMENT_AGE_AVAILABLE = SettingToggle('ENROLLMENT_AGE_AVAILABLE', default=True)


def age_available():
    return ENROLLMENT_AGE_AVAILABLE.is_enabled()
