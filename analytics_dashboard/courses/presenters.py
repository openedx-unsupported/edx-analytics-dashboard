import datetime

from django.conf import settings

from analyticsclient.client import Client
import analyticsclient.activity_type as AT


class BasePresenter(object):
    """
    This is the base class for the pages and sets up the analytics client
    for the presenters to use to access the data API.
    """

    API_DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, timeout=5):
        # API client
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)

    def parse_date(self, s):
        """
        Parse a date string to a Date object using the API date format.

        Arguments:
            s (str): Date string to parse
        """
        return datetime.datetime.strptime(s, self.API_DATE_FORMAT).date()

    def format_date(self, date):
        """
        Converts a Date object to a string using the API date format.

        Arguments:
            date (Date): Date to format
        """
        return date.strftime(self.API_DATE_FORMAT)


class CourseEngagementPresenter(BasePresenter):
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
        activities = [any_activity, ]

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


class CourseEnrollmentPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    def __init__(self, course_id, timeout=5):
        super(CourseEnrollmentPresenter, self).__init__(timeout)
        self.course_id = course_id

    def get_data(self, start_date=None, end_date=None):
        return self.client.courses(self.course_id).enrollment(start_date=start_date, end_date=end_date)

    def get_summary(self):
        """
        Returns the summary information for enrollments.

        Arguments:
            course_id (str): ID of the course to retrieve summary information of.
        """

        # Establish default return values
        data = {
            'date': None,
            'current_enrollment': None,
            'enrollment_change_last_1_days': None,
            'enrollment_change_last_7_days': None,
            'enrollment_change_last_30_days': None,
        }

        # Get most-recent enrollment
        recent_enrollment = self.get_data()

        if recent_enrollment:
            # Get data for a month prior to most-recent data
            last_enrollment_date = self.parse_date(recent_enrollment[0]['date'])
            month_before = last_enrollment_date - datetime.timedelta(days=31)
            start_date = month_before
            end_date = last_enrollment_date + datetime.timedelta(days=1)
            last_month_enrollment = self.get_data(start_date=start_date, end_date=end_date)

            # Add the first values to the returned data dictionary using the most-recent enrollment data
            current_enrollment = recent_enrollment[0]['count']
            data = {
                'date': last_enrollment_date,
                'current_enrollment': current_enrollment
            }

            # Keep track of the number of days of enrollment data, so we don't have to calculate it multiple times in
            # the loop below.
            num_days_of_data = len(last_month_enrollment)

            # Get enrollment differentials between today for yesterday, a week ago, and a month ago
            for interval in [1, 7, 30]:
                count = None
                if num_days_of_data > interval:
                    index = -interval - 1
                    count = current_enrollment - last_month_enrollment[index]['count']
                data['enrollment_change_last_%s_days' % interval] = count

        return data
