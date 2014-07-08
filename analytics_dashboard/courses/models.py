from django.conf import settings

from analyticsclient.client import Client

import analyticsclient.activity_type as AT

class StudentEngagement(object):

    def __init__(self):
        """
        Initialize StudentEngagement.
        """
        # API client
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN)

    def get_summary(self, course_id):
        """
        Retrieve all summary numbers and time.

        Arguments:
            course_id (str): ID of the course to retrieve summary information of.
        """
        course = self.client.courses(course_id)

        any_activity = course.recent_activity(AT.ANY)

        # store our activity data from the API
        activities = [any_activity,]

        # lets assume that the interval starts are the same across
        # API calls and save it so that we can display this on
        # the page
        summary = {
            'interval_end': any_activity['interval_end'],
        }

        # Create a list of data types and pass them into the recent_activity
        # call to get all the summary data that I need.
        activity_types = [AT.ATTEMPTED_PROBLEM, AT.PLAYED_VIDEO,
                          AT.POSTED_FORUM]
        for activity_type in activity_types:
            activity = course.recent_activity(activity_type)
            activities.append(activity)

        # format the data for the page
        for activity in activities:
            summary[activity['activity_type']] = activity['count']

        return summary
