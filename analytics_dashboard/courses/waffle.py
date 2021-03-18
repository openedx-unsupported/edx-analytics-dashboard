"""
This module contains various configuration toggles
for edx's analytics dashboard.
"""


from edx_toggles.toggles import NonNamespacedWaffleFlag

# .. toggle_name: display_learner_analytics
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Displays the Learner Analytics tab and links to Learner Analytics. Learner Analytics helps
#   identify which learners are active and engaged and which aren't. It also provides an overview of their daily
#   activity and their enrollment in a course. This was a rollout flag and we recommend you enable this feature.
# .. toggle_warnings: Requires the `ModuleEngagementWorkflowTask` to be run to populate the charts.
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2016-04-15
# .. toggle_target_removal_date: 2016-07-15
# .. toggle_tickets: https://github.com/edx/edx-analytics-dashboard/pull/440,
#   https://github.com/edx/edx-analytics-dashboard/pull/522
DISPLAY_LEARNER_ANALYTICS = NonNamespacedWaffleFlag(
    'display_learner_analytics', __name__)
