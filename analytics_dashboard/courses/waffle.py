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
#   activity and their enrollment in a course. This is a rollout flag and is added and enabled by default for everyone.
# .. toggle_warnings: Requires the `ModuleEngagementWorkflowTask` to be run to populate the charts.
# .. toggle_use_cases: temporary
DISPLAY_LEARNER_ANALYTICS = NonNamespacedWaffleFlag(
    'display_learner_analytics', __name__)
