from django.db import models
from django.conf import settings

from analyticsclient.client import Client
import analyticsclient.activity_type as at

class StudentEngagement(object):

    DATA_API_BASE_URL = settings.DATA_API_URL
    DATA_API_AUTH_TOKEN = settings.DATA_API_AUTH_TOKEN

    def __init__(self):
        # API client
        self.client = Client(base_url=StudentEngagement.DATA_API_BASE_URL,
                             auth_token=StudentEngagement.DATA_API_AUTH_TOKEN)

    def get_summary(self, course_id):
        course = self.client.courses(course_id)

        # get the any activity as a special case so that we can
        # get its start date
        any_activity = course.recent_activity(at.ANY)

        # store our activity data from the API
        activities = [any_activity,]

        # lets assume that the interval starts are the same across
        # API calls and save it so that we can display this on
        # the page
        summary = {
            'interval_start': any_activity['interval_start'],
        }

        # Create a list of data types and pass them into the recent_activity
        # call to get all the summary data that I need.
        # TODO: "posted_forum" for now b/c it's misspelled in activity_type.py
        activity_types = [at.ATTEMPTED_PROBLEM, at.PLAYED_VIDEO, "posted_forum"]
        for activity_type in activity_types:
            activity = course.recent_activity(activity_type)
            activities.append(activity)

        # format the data for the page
        for activity in activities:
            summary[activity['activity_type']] = activity['count']

        return summary
