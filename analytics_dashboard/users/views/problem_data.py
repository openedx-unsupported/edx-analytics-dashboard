"""
Module for views that provide info about user's interactions with problems.
"""

from .base import UsersView
from .user import SingleUserNavbarMixin


class UserProblemDataView(UsersView, SingleUserNavbarMixin):
    """
    View for page that displays a summary of a specific user's interactions with individual problems of a course.

    The summary consists of a list of problems that the user has
    attempted and specifies the total number of attempts and the final
    score for each problem.

    For each problem, the final score combines the most recent score
    obtained with the maximum possible score (e.g., 7/10).
    """
    course_api_client = None

    template_name = 'users/problem_data.html'

    active_primary_nav_item = 'problems'

    def get_context_data(self, **kwargs):
        """
        Add summary of problem data for requested course and user to template context.

        If enabled, make use of course API to obtain descriptive names for problems to list.
        """
        context = super(UserProblemDataView, self).get_context_data(**kwargs)

        # If course API is enabled, obtain info about blocks
        if self.course_api_enabled:
            blocks = self.course_structure.get('blocks', {})
        else:
            blocks = {}

        # Prepare for retrieving weekly problem data by looking up user ID
        username = kwargs['username']
        profile = self.client.users(username).profile()
        user_id = profile['id']

        # Retrieve weekly problem data
        weekly_problem_data = self.client.user_problem_weekly_data(self.course_id, user_id).weekly_problem_data()

        # Summarize weekly problem data
        problem_data = {}

        for entry in weekly_problem_data:
            week_ending = entry['week_ending']
            problem_id = entry['problem_id']
            num_attempts = entry['num_attempts']
            final_score = '{}/{}'.format(entry['most_recent_score'], entry['max_score'])
            # We'd like to display a descriptive name for the problem belonging to this entry.
            # If that's not available, fall back on problem ID:
            problem_name = blocks.get(problem_id, {}).get('display_name', problem_id)

            if problem_id not in problem_data:
                # Summary doesn't have an entry for this problem, so insert relevant data as is
                problem_data[problem_id] = {
                    'week_ending': week_ending,
                    'name': problem_name,
                    'num_attempts': num_attempts,
                    'final_score': final_score,
                }
            else:
                # Summary already has an entry for this problem, so:
                problem = problem_data[problem_id]
                # - Increment total number of attempts
                problem['num_attempts'] += num_attempts
                # - Update final score
                #   (this is only necessary if the problem data we are looking at belongs to a more recent week)
                if week_ending > problem['week_ending']:
                    problem['week_ending'] = week_ending
                    problem['final_score'] = final_score
                problem_data[problem_id] = problem

        context['username'] = username
        context['problem_data'] = problem_data.values()

        return context
