"""
This module contains various configuration toggles
for edx's analytics dashboard.
"""


from edx_toggles.toggles import NonNamespacedWaffleFlag

# .. toggle_name: display_learner_analytics
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Display Learner Analytics links
# .. toggle_use_cases: opt_in
DISPLAY_LEARNER_ANALYTICS = NonNamespacedWaffleFlag(
    'display_learner_analytics', __name__)
