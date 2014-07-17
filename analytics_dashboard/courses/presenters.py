import datetime

from django.conf import settings

from analyticsclient.client import Client
import analyticsclient.activity_type as AT


class BaseStudent(object):
    """
    This is the base class for the pages and sets up the analytics client
    for the presenters to use to access the data API.
    """

    def __init__(self):
        # API client
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=5)

class StudentEngagement(BaseStudent):
    """
    Presenter for the engagement page.
    """

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

        # let's assume that the interval starts are the same across
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

class StudentEnrollment(BaseStudent):
    """
    Presenter for the enrollment page.
    """

    # this is the date format expected from the API
    DATE_FORMAT = '%Y-%m-%d'

    def get_summary(self, course_id):
        """
        Returns the summary information for enrollments.

        Arguments:
            course_id (str): ID of the course to retrieve summary information of.
        """

        # By default, get the activity of the most recent day or None if
        # not available.
        total_enrollment_trend = self.get_enrollment_trend(course_id)

        # date ranges to show summaries of
        days_past = (2, 8, 31)

        # use the end date from the most recent enrollment trend or None
        if len(total_enrollment_trend) == 0:
            total_enrollment = None
            display_date_end = None
            # Add an item set to None for each value of days_past.
            enrollments = [None]*len(days_past)
        else:
            total_enrollment = total_enrollment_trend[0]['count']
            display_date_end = self.parse_enrollment_date(
                total_enrollment_trend[0])
            # the api's end date is exclusive, so we need to increment by a day
            end_date = display_date_end + datetime.timedelta(days=1)
            enrollments = self.get_enrollment_change(course_id, end_date,
                                                     days_past)

        return {
            'date_end': self.get_date_string_or_none(display_date_end),
            'total_enrollment': total_enrollment,
            'enrollment_change_yesterday': enrollments[0],
            'enrollment_change_last_7_days': enrollments[1],
            'enrollment_change_last_30_days': enrollments[2],
        }


    def get_enrollment_change(self, course_id, end_date, days_past):
        """
        Returns an array of the change in enrollments for the specified days_past.
        None will be returned if date doesn't exist for the entire date range

        Arguments:
            course_id (str): ID of the course to retrieve summary information of.
            end_date (Date): Optional date that is used as the ending date.
            days_past (int): Days worth of data to get in the past.
        """
        enrollment_change = []

        # make a single call to get the trend for the largest date range
        max_trend_enrollments = self.get_enrollment_trend(course_id, end_date,
                                                          max(days_past))

        max_trend_counts = [count['count'] for count in max_trend_enrollments]
        for past in days_past:
            # slice off the ends from the longest date range to compute trends
            trend = max_trend_counts[-past:]

            # check to make sure that we got trend data for the range requested
            if len(trend) < past:
                enrollment_change.append(None)
            else:
                enrollment_change.append(self.calculate_trend_difference(trend))

        return enrollment_change

    def get_enrollment_trend(self, course_id, end_date=None, days_past=1):
        """
        Returns a list of dictionaries of the enrollment trend data:
        {count: #, date: yyyy-mm-dd}

        Arguments:
            course_id (str): ID of the course to retrieve summary information of.
            end_date (Date): Optional date that is used as the ending date.
            days_past (int): Days worth of data to get in the past.
        """
        start_date = None
        if end_date is not None:
            start_date = end_date - datetime.timedelta(days=days_past)

        # get string representations of the data to pass to the api client
        start_date_param = self.get_date_string_or_none(start_date)
        end_date_param = self.get_date_string_or_none(end_date)

        course = self.client.courses(course_id)
        enrollments = course.enrollment(None, start_date_param, end_date_param)
        # sort the enrollments by date (past to most recent)
        sorted_enrollments = sorted(enrollments,
                                    key=lambda x: self.parse_enrollment_date(x))

        return sorted_enrollments


    def get_date_string_or_none(self, date):
        """
        Returns a string (yyyy-mm-dd) representation of the date or None.

        Arguments:
            date (Date): Date to convert to a string.
        """
        date_param = None
        if date is not None:
            date_param = date.strftime(StudentEnrollment.DATE_FORMAT)
        return date_param

    def parse_enrollment_date(self, enrollment):
        """
        Parse a date string to a Date object.

        Arguments:
            enrollment (Dict): Dictionary that has a 'date' field with date string (yyyy-mm-dd).
        """
        return datetime.datetime.strptime(enrollment['date'],
                                          StudentEnrollment.DATE_FORMAT).date()


    def calculate_trend_difference(self, counts):
        """
        Returns the overall change in number of enrollments, assuming that the first
        count is the farthest in the past.

        Arguments:
            counts (List): List of ints.
        """
        if len(counts) < 2:
            raise ValueError(
                'More than two counts are needed to calculate the difference.')

        return counts[-1] - counts[0]
