import datetime

from django.conf import settings

from analyticsclient.client import Client
import analyticsclient.constants.activity_type as AT
from analyticsclient.constants import demographic

from waffle import switch_is_active


class BasePresenter(object):
    """
    This is the base class for the pages and sets up the analytics client
    for the presenters to use to access the data API.
    """
    default_date_interval = 60

    def __init__(self, course_id, timeout=5):
        # API client
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)
        self.course_id = course_id
        self.course = self.client.courses(self.course_id)
        self.date_format = Client.DATE_FORMAT
        self.date_time_format = Client.DATETIME_FORMAT

    def parse_date(self, date_string):
        """
        Parse a date string to a Date object using the API date format.

        Arguments:
            date_string (str): Date string to parse
        """
        return datetime.datetime.strptime(date_string, self.date_format).date()

    def format_date(self, date):
        """
        Converts a Date object to a string using the API date format.

        Arguments:
            date (Date): Date to format
        """
        return date.strftime(self.date_format)

    def parse_date_time_as_date(self, date_time_string):
        """
        Parse a date time string to a Date object.

        Arguments:
            date_time_string (str): Date time string to parse
        """
        return datetime.datetime.strptime(date_time_string, self.date_time_format).date()

    def get_date_range(self, interval_end=None, num_days=None):
        """
        Returns a start and end date that span the interval specified.  If
        interval_end is None, both start_date and end_date are returned as None.
        """
        start_date = None
        end_date = None
        if interval_end is not None:
            if num_days is None:
                num_days = self.default_date_interval
            start_date = interval_end - datetime.timedelta(days=num_days)
            end_date = interval_end + datetime.timedelta(days=1)
        return start_date, end_date


class CourseEngagementPresenter(BasePresenter):
    """
    Presenter for the engagement page.
    """

    def get_trend_data(self, end_date=None, num_days=None):
        """
        Retrieve engagement activity trends for specified date range and return
        results with zeros filled in for all activities.
        """
        start_date, end_date = self.get_date_range(end_date, num_days)
        api_trends = self.course.activity(start_date=start_date, end_date=end_date)

        # feature gate posted_forum.  If enabled, the forum will be rendered in the engagement page
        trend_types = [AT.ANY, AT.PLAYED_VIDEO, AT.ATTEMPTED_PROBLEM]
        if switch_is_active('show_engagement_forum_activity'):
            trend_types.append(AT.POSTED_FORUM)

        # fill in gaps in activity with zero for display (api doesn't return
        # the field if no data exists for it, so we fill in the zeros here)
        trends = []
        for datum in api_trends:
            trend_week = {'weekEnding': self.format_date(self.parse_date_time_as_date(datum['interval_end']))}
            for trend_type in trend_types:
                trend_week[trend_type] = datum[trend_type] if trend_type in datum else 0
            trends.append(trend_week)

        return trends

    def get_summary(self):
        """
        Retrieve all summary numbers and week ending time.
        """
        # store our activity data from the API
        api_activity = self.course.activity()[0]
        summary = {'interval_end': self.parse_date_time_as_date(api_activity['interval_end'])}

        # fill in gaps in the summary if no data found so we can display a proper message
        activity_types = [AT.ANY, AT.ATTEMPTED_PROBLEM, AT.PLAYED_VIDEO, AT.POSTED_FORUM]
        for activity_type in activity_types:
            if activity_type in api_activity:
                summary[activity_type] = api_activity[activity_type]
            else:
                summary[activity_type] = None

        return summary


class CourseEnrollmentPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    def get_trend_data(self, end_date=None, num_days=None):
        start_date, end_date = self.get_date_range(end_date, num_days)
        return self.course.enrollment(start_date=start_date, end_date=end_date)

    def get_geography_data(self):
        """
        Returns a list of course geography data and the updated date (ex. 2014-1-31).
        """
        api_response = self.course.enrollment(demographic.LOCATION)
        data = []
        update_date = None
        summary = {}

        if api_response:
            update_date = api_response[0]['date']

            # Sort data by descending enrollment count
            api_response = sorted(api_response, key=lambda i: i['count'], reverse=True)

            # get the sum as a float so we can divide by it to get a percent
            total_enrollment = float(sum([datum['count'] for datum in api_response]))

            # formatting this data for easy access in the table UI
            data = [{'countryCode': datum['country']['alpha3'],
                     'countryName': datum['country']['name'],
                     'count': datum['count'],
                     'percent': datum['count'] / total_enrollment if total_enrollment > 0 else 0.0}
                    for datum in api_response if datum['country']['name'] != 'UNKNOWN']

            # Include a summary of the number of countries and the top 3 countries.
            summary = {
                'num_countries': len(data),
                'top_countries': []
            }
            for i in range(0, 3):
                summary['top_countries'].append(data[i])

        return data, update_date, summary

    def get_summary(self):
        """
        Returns the summary information for enrollments.
        """

        # Establish default return values
        data = {
            'date': None,
            'current_enrollment': None,
            'enrollment_change_last_7_days': None,
        }

        # Get most-recent enrollment
        recent_enrollment = self.get_trend_data()

        if recent_enrollment:
            # Get data for a month prior to most-recent data
            days_in_week = 7
            last_enrollment_date = self.parse_date(recent_enrollment[0]['date'])
            last_week_enrollment = self.get_trend_data(end_date=last_enrollment_date, num_days=days_in_week)

            # Add the first values to the returned data dictionary using the most-recent enrollment data
            current_enrollment = recent_enrollment[0]['count']
            data = {
                'date': last_enrollment_date,
                'current_enrollment': current_enrollment
            }

            # we could get fewer days of data than desired
            num_days_of_data = len(last_week_enrollment)

            # Get difference in enrollment for last week
            count = None
            if num_days_of_data > days_in_week:
                index = -days_in_week - 1
                count = current_enrollment - last_week_enrollment[index]['count']
            data['enrollment_change_last_%s_days' % days_in_week] = count

        return data
