import datetime
import logging

from django.utils.translation import ugettext as _
from django.conf import settings
from django_countries import countries
from waffle import switch_is_active
from analyticsclient.client import Client
import analyticsclient.constants.activity_type as AT
from analyticsclient.constants import demographic, UNKNOWN_COUNTRY_CODE


logger = logging.getLogger(__name__)
COUNTRIES = dict(countries)


class BasePresenter(object):
    """
    This is the base class for the pages and sets up the analytics client
    for the presenters to use to access the data API.
    """

    def __init__(self, course_id, timeout=5):
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)
        self.course_id = course_id
        self.course = self.client.courses(self.course_id)

    @staticmethod
    def parse_api_date(s):
        """ Parse a string according to the API date format. """
        return datetime.datetime.strptime(s, Client.DATE_FORMAT).date()

    @staticmethod
    def parse_api_datetime(s):
        """ Parse a string according to the API datetime format. """
        return datetime.datetime.strptime(s, Client.DATETIME_FORMAT)

    @staticmethod
    def strip_time(s):
        return s[:-7]


class CourseEngagementPresenter(BasePresenter):
    """
    Presenter for the engagement page.
    """

    def get_activity_types(self):
        activities = [AT.ANY, AT.PLAYED_VIDEO, AT.ATTEMPTED_PROBLEM]

        # Include forum activity only if feature is enabled.
        if switch_is_active('show_engagement_forum_activity'):
            activities.append(AT.POSTED_FORUM)

        return activities

    def _build_trend(self, api_trends):
        """
        Format activity trends for specified date range and return results with
        zeros filled in for all activities.
        """
        trend_types = self.get_activity_types()

        # fill in gaps in activity with zero for display (api doesn't return
        # the field if no data exists for it, so we fill in the zeros here)
        trends = []
        for datum in api_trends:
            # convert end of interval to ending day of week
            interval_end = self.parse_api_datetime(datum['interval_end'])
            week_ending = interval_end.date() - datetime.timedelta(days=1)
            trend_week = {'weekEnding': week_ending.isoformat()}
            for trend_type in trend_types:
                trend_week[trend_type] = datum[trend_type] or 0
            trends.append(trend_week)

        return trends

    def _build_summary(self, api_trends):
        """
        Format all summary numbers and week ending time.
        """

        most_recent = api_trends[-1]
        summary = {
            'last_updated': self.parse_api_datetime(most_recent['created'])
        }

        # Fill in gaps in the summary if no data found so we can display a proper message
        activity_types = self.get_activity_types()
        for activity_type in activity_types:
            if activity_type in most_recent:
                summary[activity_type] = most_recent[activity_type]
            else:
                summary[activity_type] = None

        return summary

    def get_summary_and_trend_data(self):
        """
        Retrieve recent summary and all historical trend data.
        """
        now = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        api_trends = self.course.activity(start_date=None, end_date=now)
        summary = self._build_summary(api_trends)
        trends = self._build_trend(api_trends)
        return summary, trends


class CourseEnrollmentPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    NUMBER_TOP_COUNTRIES = 3

    def get_summary_and_trend_data(self):
        """
        Retrieve recent summary and all historical trend data.
        """
        now = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        trends = self.course.enrollment(start_date=None, end_date=now)
        summary = self._build_summary(trends)
        return summary, trends

    def _translate_country_names(self, data):
        """ Translate full country name from English to the language of the logged in user. """

        for datum in data:
            if datum['country']['name'] == UNKNOWN_COUNTRY_CODE:
                # Translators: This is a placeholder for enrollment data collected without a known geolocation.
                datum['country']['name'] = _('Unknown Country')
            else:
                country_code = datum['country']['alpha3']

                try:
                    datum['country']['name'] = unicode(COUNTRIES[datum['country']['alpha2']])
                except KeyError:
                    logger.warning('Unable to locate %s in django_countries.', country_code)

        return data

    def get_geography_data(self):
        """
        Returns a list of course geography data and the updated date (ex. 2014-1-31).
        """
        api_response = self.course.enrollment(demographic.LOCATION)
        data = []
        summary = {}

        if api_response:
            last_updated = self.parse_api_datetime(api_response[0]['created'])

            # Sort data by descending enrollment count
            api_response = sorted(api_response, key=lambda i: i['count'], reverse=True)

            # Translate the country names
            api_response = self._translate_country_names(api_response)

            # get the sum as a float so we can divide by it to get a percent
            total_enrollment = float(sum([datum['count'] for datum in api_response]))

            # formatting this data for easy access in the table UI
            data = [{'countryCode': datum['country']['alpha3'],
                     'countryName': datum['country']['name'],
                     'count': datum['count'],
                     'percent': datum['count'] / total_enrollment if total_enrollment > 0 else 0.0}
                    for datum in api_response]

            # Filter out the unknown entry for the summary data
            data_without_unknown = [datum for datum in data if datum['countryCode'] is not None]

            # Include a summary of the number of countries and the top 3 countries, excluding unknown.
            summary = {
                'last_updated': last_updated,
                'num_countries': len(data_without_unknown),
                'top_countries': data_without_unknown[:self.NUMBER_TOP_COUNTRIES]
            }

        return summary, data

    def _build_summary(self, api_trends):
        """
        Build summary information for enrollments from trends.
        """

        # Establish default return values
        data = {
            'last_updated': None,
            'current_enrollment': None,
            'enrollment_change_last_7_days': None,
        }

        if api_trends:
            # Get most-recent enrollment
            recent_enrollment = api_trends[-1]

            # Get data for a month prior to most-recent data
            days_in_week = 7
            last_enrollment_date = self.parse_api_datetime(recent_enrollment['created'])

            # Add the first values to the returned data dictionary using the most-recent enrollment data
            current_enrollment = recent_enrollment['count']
            data = {
                'last_updated': last_enrollment_date,
                'current_enrollment': current_enrollment
            }

            # Get difference in enrollment for last week
            count = None
            if len(api_trends) > days_in_week:
                index = -days_in_week - 1
                count = current_enrollment - api_trends[index]['count']
            data['enrollment_change_last_%s_days' % days_in_week] = count

        return data
