"""
This module contains various configuration toggles
for edx's analytics dashboard.
"""


from edx_toggles.toggles import NonNamespacedWaffleFlag, SettingToggle

# .. toggle_name: display_learner_analytics
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Displays the Learner Analytics tab and links to Learner Analytics. Learner Analytics helps
#   identify which learners are active and engaged and which aren't. It also provides an overview of their daily
#   activity and their enrollment in a course. This was a rollout flag and we recommend you enable this feature.
# .. toggle_warning: Requires the `ModuleEngagementWorkflowTask` to be run to populate the charts.
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2016-04-15
# .. toggle_target_removal_date: 2016-07-15
# .. toggle_tickets: https://github.com/edx/edx-analytics-dashboard/pull/440,
#   https://github.com/edx/edx-analytics-dashboard/pull/522
DISPLAY_LEARNER_ANALYTICS = NonNamespacedWaffleFlag(
    'display_learner_analytics', __name__)

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
