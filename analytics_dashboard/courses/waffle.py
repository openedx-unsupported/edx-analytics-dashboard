"""
This module contains various configuration toggles
for edx's analytics dashboard.
"""


from edx_toggles.toggles import NonNamespacedWaffleFlag

# .. toggle_name: display_learner_analytics
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Allows specified users to view Learner Analytics. Also displays the Learner Analytics tab and
#   links to Learner Analytics on the Course Home page. Learner Analytics helps identify which learners are active and
#   engaged and which aren't. It also provides an overview of their daily activity and their enrollment in a course.
# .. toggle_warnings: Requires the `ModuleEngagementWorkflowTask` to be run to populate the charts.
# .. toggle_use_cases: opt_in
DISPLAY_LEARNER_ANALYTICS = NonNamespacedWaffleFlag(
    'display_learner_analytics', __name__)
