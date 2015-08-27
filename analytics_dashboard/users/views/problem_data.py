from .base import UsersView
from .user import SingleUserNavbarMixin


class UserProblemDataView(UsersView, SingleUserNavbarMixin):
    course_api_client = None

    template_name = 'users/problem_data.html'

    active_primary_nav_item = 'problems'

    def get_context_data(self, **kwargs):
        context = super(UserProblemDataView, self).get_context_data(**kwargs)

        if self.course_api_enabled:
            blocks = self.course_structure.get('blocks', {})
        else:
            blocks = {}

        username = kwargs['username']
        profile = self.client.users(username).profile()
        user_id = profile['id']

        weekly_problem_data = self.client.user_problem_weekly_data(self.course_id, user_id).weekly_problem_data()

        problem_data = {}

        for entry in weekly_problem_data:
            week_ending = entry['week_ending']
            problem_id = entry['problem_id']
            num_attempts = entry['num_attempts']
            final_score = '{}/{}'.format(entry['most_recent_score'], entry['max_score'])
            problem_name = blocks.get(problem_id, {}).get('display_name', problem_id)

            if problem_id not in problem_data:
                problem_data[problem_id] = {
                    'week_ending': week_ending,
                    'name': problem_name,
                    'num_attempts': num_attempts,
                    'final_score': final_score,
                }
            else:
                problem = problem_data[problem_id]
                problem['num_attempts'] += num_attempts
                if week_ending > problem['week_ending']:
                    problem['week_ending'] = week_ending
                    problem['final_score'] = final_score
                problem_data[problem_id] = problem

        context['username'] = username
        context['problem_data'] = problem_data.values()

        return context
