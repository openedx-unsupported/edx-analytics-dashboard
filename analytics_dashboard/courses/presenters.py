import copy
import datetime
import logging

from collections import namedtuple

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_countries import countries
from waffle import switch_is_active
from analyticsclient.client import Client
import analyticsclient.constants.activity_type as AT
import analyticsclient.constants.education_level as EDUCATION_LEVEL
import analyticsclient.constants.gender as GENDER
from analyticsclient.constants import demographic, UNKNOWN_COUNTRY_CODE, enrollment_modes
from analyticsclient.exceptions import NotFoundError

import courses.utils as utils


logger = logging.getLogger(__name__)

KNOWN_GENDERS = [GENDER.FEMALE, GENDER.MALE, GENDER.OTHER]
GENDERS = KNOWN_GENDERS + [GENDER.UNKNOWN]


# for display
GENDER_FULL_NAMES = {
    GENDER.FEMALE: _('Female'),
    GENDER.MALE: _('Male'),
    # Translators: Other gender
    GENDER.OTHER: _('Other'),
    # Translators: Unknown gender
    GENDER.UNKNOWN: _('Unknown')
}

GENDER_ORDER = {
    GENDER.FEMALE: 0,
    GENDER.MALE: 1,
    GENDER.OTHER: 2
}

KNOWN_EDUCATION_LEVELS = [EDUCATION_LEVEL.NONE, EDUCATION_LEVEL.OTHER, EDUCATION_LEVEL.PRIMARY,
                          EDUCATION_LEVEL.JUNIOR_SECONDARY, EDUCATION_LEVEL.SECONDARY, EDUCATION_LEVEL.ASSOCIATES,
                          EDUCATION_LEVEL.BACHELORS, EDUCATION_LEVEL.MASTERS, EDUCATION_LEVEL.DOCTORATE]
# for display
EDUCATION_NAMES = {
    # Translators: This describes the learner's education level.
    EDUCATION_LEVEL.NONE: _('None'),
    # Translators: This describes the learner's education level.
    EDUCATION_LEVEL.OTHER: _('Other'),
    # Translators: This describes the learner's education level (e.g. Elementary School Degree).
    EDUCATION_LEVEL.PRIMARY: _('Primary'),
    # Translators: This describes the learner's education level  (e.g. Middle School Degree).
    EDUCATION_LEVEL.JUNIOR_SECONDARY: _('Middle'),
    # Translators: This describes the learner's education level.
    EDUCATION_LEVEL.SECONDARY: _('Secondary'),
    # Translators: This describes the learner's education level (e.g. Associate's Degree).
    EDUCATION_LEVEL.ASSOCIATES: _("Associate"),
    # Translators: This describes the learner's education level (e.g. Bachelor's Degree).
    EDUCATION_LEVEL.BACHELORS: _("Bachelor's"),
    # Translators: This describes the learner's education level (e.g. Master's Degree).
    EDUCATION_LEVEL.MASTERS: _("Master's"),
    # Translators: This describes the learner's education level (e.g. Doctorate Degree).
    EDUCATION_LEVEL.DOCTORATE: _('Doctorate')
}

# Translators: This describes the learner's education level.
UNKNOWN_EDUCATION_LEVEL_NAME = _('Unknown')

# order for displaying in the chart
EDUCATION_ORDER = {
    EDUCATION_LEVEL.NONE: 0,
    EDUCATION_LEVEL.PRIMARY: 1,
    EDUCATION_LEVEL.JUNIOR_SECONDARY: 2,
    EDUCATION_LEVEL.SECONDARY: 3,
    EDUCATION_LEVEL.ASSOCIATES: 4,
    EDUCATION_LEVEL.BACHELORS: 5,
    EDUCATION_LEVEL.MASTERS: 6,
    EDUCATION_LEVEL.DOCTORATE: 7,
    EDUCATION_LEVEL.OTHER: 8,
}


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

    def get_current_date(self):
        return datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)

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

    @staticmethod
    def sum_counts(data):
        return sum(datum['count'] for datum in data)


# stores the answer distribution return from CoursePerformancePresenter
AnswerDistributionEntry = namedtuple('AnswerDistributionEntry',
                                     'last_updated, questions, active_question, answer_distribution, '
                                     'answer_distribution_limited, is_random, answer_type, problem_part_description')


class CoursePerformancePresenter(BasePresenter):
    """
    Presenter for the performance page.
    """

    # limit for the number of bars to display in the answer distribution chart
    CHART_LIMIT = 12

    def get_answer_distribution(self, problem_id, problem_part_id):
        """
        Retrieve answer distributions for a particular module/problem and problem part.
        """

        module = self.client.modules(self.course_id, problem_id)

        api_response = module.answer_distribution()
        questions = self._build_questions(api_response)

        filtered_active_question = [i for i in questions if i['part_id'] == problem_part_id]
        if len(filtered_active_question) is 0:
            raise NotFoundError
        else:
            active_question = filtered_active_question[0]['question']

        answer_distributions = self._build_answer_distribution(api_response, problem_part_id)
        problem_part_description = self._build_problem_description(problem_part_id, questions)

        is_random = self._is_answer_distribution_random(answer_distributions)
        answer_distribution_limited = None
        if not is_random:
            # only display the top in the chart
            answer_distribution_limited = answer_distributions[:self.CHART_LIMIT]

        answer_type = self._get_answer_type(answer_distributions)
        last_updated = self.parse_api_datetime(answer_distributions[0]['created'])

        return AnswerDistributionEntry(last_updated, questions, active_question, answer_distributions,
                                       answer_distribution_limited, is_random, answer_type, problem_part_description)

    def _build_problem_description(self, problem_part_id, questions):
        """ Returns the displayable problem name. """
        problem = [q for q in questions if q['part_id'] == problem_part_id][0]
        if problem['problem_name']:
            return u'{0} - {1}'.format(problem['problem_name'], problem['question'])
        return problem['question']

    def _get_answer_type(self, answer_distributions):
        """ Returns either answer_value_text or answer_value_numeric. """

        # answer field for numeric values returned from API
        numeric_field = 'answer_value_numeric'
        # answer field for text values returned from API
        text_field = 'answer_value_text'

        # returns the first field found to be filled
        for ad in answer_distributions:
            if ad[numeric_field] is not None:
                return numeric_field
            elif ad[text_field] is not None:
                return text_field

        # default to text answer if both fields were null/none
        return text_field

    def _is_answer_distribution_random(self, answer_distributions):
        """
        Problems are considered randomized if variant is populated with values
        greater than 1.
        """
        for ad in answer_distributions:
            variant = ad['variant']
            if variant is not None and variant is not 1:
                return True
        return False

    def _build_questions(self, answer_distributions):
        """
        Builds the questions and part_id from the answer distribution. Displayed
        drop down.
        """
        questions = []
        part_id_to_problem = {}

        # Collect unique questions from the answer distribution
        for question_answer in answer_distributions:
            question = question_answer.get('question_text', None)
            problem_name = question_answer.get('problem_display_name', None)
            part_id_to_problem[question_answer['part_id']] = {
                'question': question,
                'problem_name': problem_name
            }

        for part_id, problem in part_id_to_problem.iteritems():
            questions.append({
                'part_id': part_id,
                'question': problem['question'],
                'problem_name': problem['problem_name']
            })

        utils.sorting.natural_sort(questions, 'part_id')

        # add an enumerated label
        for i, question in enumerate(questions):
            text = question['question']
            question_num = i + 1
            if text:
                text = u'Submissions for Part {0}: {1}'.format(question_num, text)
            else:
                text = u'Submissions for Part {0}'.format(question_num)
            question['question'] = text

        return questions

    def _build_answer_distribution(self, api_response, problem_part_id):
        """ Filter for this problem part and sort descending order. """
        answer_distributions = [i for i in api_response if i['part_id'] == problem_part_id]
        answer_distributions = sorted(answer_distributions, key=lambda a: -a['count'])
        return answer_distributions


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

    def _build_trend_week(self, trend_types, week_ending, api_trend):
        trend_week = {'weekEnding': week_ending.isoformat()}
        for trend_type in trend_types:
            if trend_type in api_trend:
                trend_week[trend_type] = api_trend[trend_type] or 0
            else:
                trend_week[trend_type] = 0
        return trend_week

    def _build_trend(self, api_trends):
        """
        Format activity trends for specified date range and return results with
        zeros filled in for all activities.
        """
        trend_types = self.get_activity_types()
        trends = []

        # add zeros for the week prior if we only have a single point (prevents just a single point in the chart)
        if len(api_trends) == 1:
            interval_end = self.parse_api_datetime(api_trends[0]['interval_end'])
            week_ending = interval_end.date() - datetime.timedelta(days=8)
            trends.append(self._build_trend_week(trend_types, week_ending, {}))

        # fill in gaps in activity with zero for display (api doesn't return
        # the field if no data exists for it, so we fill in the zeros here)
        for datum in api_trends:
            # convert end of interval to ending day of week
            interval_end = self.parse_api_datetime(datum['interval_end'])
            week_ending = interval_end.date() - datetime.timedelta(days=1)
            trends.append(self._build_trend_week(trend_types, week_ending, datum))

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
        api_trends = self.course.activity(start_date=None, end_date=self.get_current_date())
        summary = self._build_summary(api_trends)
        trends = self._build_trend(api_trends)
        return summary, trends


class CourseEnrollmentPresenter(BasePresenter):
    """ Presenter for the course enrollment data. """

    NUMBER_TOP_COUNTRIES = 3

    @property
    def display_verified_enrollment(self):
        return switch_is_active('display_verified_enrollment')

    def get_summary_and_trend_data(self):
        """
        Retrieve recent summary and all historical trend data.
        """
        _demographic = 'mode' if self.display_verified_enrollment else None
        trends = self.course.enrollment(_demographic, start_date=None, end_date=self.get_current_date())
        trends = self._fill_trend(trends)

        summary = self._build_summary(trends)

        # add zero for the day prior (prevents just a single point in the chart)
        if len(trends) == 1:
            day_before = self.parse_api_date(trends[0]['date']) - datetime.timedelta(days=1)
            trends.insert(0, self._create_empty_enrollment_datapoint(day_before))

        if self.display_verified_enrollment:
            trends = self._merge_audit_and_honor(trends)
            summary, trends = self._remove_empty_enrollment_modes(summary, trends)

        return summary, trends

    def _get_valid_enrollment_modes(self, trends):
        """
        Return enrollment modes for which there is currently, or have been in the past, at least one enrolled student.
        """
        valid_modes = {enrollment_modes.AUDIT, enrollment_modes.HONOR}
        invalid_modes = set(enrollment_modes.ALL) - valid_modes

        for datum in trends:
            for candidate in invalid_modes.copy():
                if datum.get(candidate, 0) > 0:
                    invalid_modes.remove(candidate)
                    valid_modes.add(candidate)

            if len(invalid_modes) == 0:
                break

        return valid_modes

    def _remove_empty_enrollment_modes(self, summary, trends):
        """
        Based on the trend data, identify enrollment modes with no enrollments and remove them from display.
        """
        valid_modes = self._get_valid_enrollment_modes(trends)
        invalid_modes = set(enrollment_modes.ALL) - valid_modes

        for trend in trends:
            for mode in invalid_modes:
                trend.pop(mode, None)

        if enrollment_modes.VERIFIED not in valid_modes:
            summary.pop('verified_enrollment')
            summary.pop('verified_change_last_7_days')

        return summary, trends

    def _merge_audit_and_honor(self, data):
        """
        Merge the audit and honor tracks into a single "honor" track

        Note: This can be removed once the API has been deployed, as it will be updated to handle this for us.
        """
        for datum in data:
            datum[enrollment_modes.HONOR] = datum.get(enrollment_modes.HONOR, 0) + datum.pop(enrollment_modes.AUDIT, 0)

        return data

    def _fill_trend(self, api_response):
        """ Fills in enrollment counts for missing days in the trend data for display. """
        if api_response:
            start_date = self.parse_api_date(api_response[0]['date'])
            end_date = self.parse_api_date(api_response[-1]['date'])
            days_apart = (end_date - start_date).days

            for day_change in range(days_apart):
                expected_date = start_date + datetime.timedelta(days=day_change)
                current_date = self.parse_api_date(api_response[day_change]['date'])

                if current_date > expected_date:
                    api_response.insert(day_change, self._clone_datapoint(api_response[day_change - 1], expected_date))

        return api_response

    def _clone_datapoint(self, datapoint, new_date):
        """
        Clones a datapoint, replacing the date with the date specified
        """
        datapoint = copy.copy(datapoint)
        datapoint['date'] = new_date.isoformat()
        return datapoint

    def _create_empty_enrollment_datapoint(self, day):
        """
        Create an enrollment datapoint with all counts set to zero.
        """
        trend = {'date': day.isoformat(), 'count': 0}

        if self.display_verified_enrollment:
            for mode in enrollment_modes.ALL:
                trend[mode] = 0

        return trend

    def _translate_country_names(self, data):
        """ Translate full country name from English to the language of the logged in user. """

        # Instantiate this variable here, instead of at the top of the file,
        # to ensure the user's language has been set.
        _countries = dict(countries.countries)

        for datum in data:
            if datum['country']['name'] == UNKNOWN_COUNTRY_CODE:
                # Translators: This is a placeholder for enrollment data collected without a known geolocation.
                datum['country']['name'] = _('Unknown Country')
            else:
                country_code = datum['country']['alpha3']

                try:
                    datum['country']['name'] = unicode(_countries[datum['country']['alpha2']])
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
            total_enrollment = self.sum_counts(api_response)

            # formatting this data for easy access in the table UI
            data = [{'countryCode': datum['country']['alpha3'],
                     'countryName': datum['country']['name'],
                     'count': datum['count'],
                     'percent': utils.math.calculate_percent(datum['count'], total_enrollment)}
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
            'verified_enrollment': None,
            'verified_change_last_7_days': None,
        }

        if api_trends:
            # Get most-recent enrollment
            recent_enrollment = api_trends[-1]

            # Get data for a month prior to most-recent data
            days_in_week = 7
            last_enrollment_date = self.parse_api_datetime(recent_enrollment['created'])

            # Add the first values to the returned data dictionary using the most-recent enrollment data
            current_enrollment = recent_enrollment['count']
            verified_enrollment = recent_enrollment.get(enrollment_modes.VERIFIED,
                                                        0) if self.display_verified_enrollment else None

            data = {
                'last_updated': last_enrollment_date,
                'current_enrollment': current_enrollment,
                'verified_enrollment': verified_enrollment
            }

            # Get difference in enrollment for last week
            count = None
            verified_count = None

            if len(api_trends) > days_in_week:
                index = -days_in_week - 1
                count = current_enrollment - api_trends[index]['count']
                if self.display_verified_enrollment:
                    verified_count = verified_enrollment - api_trends[index].get(enrollment_modes.VERIFIED, 0)

            data['enrollment_change_last_%s_days' % days_in_week] = count

            if self.display_verified_enrollment:
                data['verified_change_last_%s_days' % days_in_week] = verified_count

        return data


class CourseEnrollmentDemographicsPresenter(BasePresenter):
    """ Presenter for course enrollment demographic data. """

    # ages at this and above will be binned
    MAX_AGE = 100

    def get_gender(self):
        """
        Returns the updated time, most recent gender counts, and breakdown of daily
        gender trends.
        """
        api_response = self.course.enrollment(demographic.GENDER, end_date=self.get_current_date())
        recent_genders = None
        trend = None
        last_updated = None
        known_enrollment_percent = None

        if api_response:
            last_updated = self.parse_api_datetime(api_response[-1]['created'])
            recent_genders = self._build_recent_genders(api_response)
            trend = self._build_gender_trend(api_response)
            known_enrollment_percent = self._build_gender_known_percent(api_response)

        return last_updated, recent_genders, trend, known_enrollment_percent

    def _build_gender_trend(self, api_response):
        """ Adds the 'total' enrollment to the trend, including unknown (not reported) genders. """
        genders = GENDERS

        for enrollment in api_response:
            enrollment['total'] = self._calculate_sum(enrollment, genders)
            # fill in null/None genders so 0 is displayed
            for gender in genders:
                if not enrollment[gender]:
                    enrollment[gender] = 0
        return api_response

    def _build_recent_genders(self, api_response):
        """ Returns the most recent gender percentages (does not include unknown (not reported). """
        genders = KNOWN_GENDERS
        recent_genders = []
        most_recent_data = api_response[-1]
        total_enrollment = self._calculate_sum(most_recent_data, genders)
        for gender in genders:
            recent_genders.append({
                'gender': GENDER_FULL_NAMES[gender],
                'percent': utils.math.calculate_percent(most_recent_data[gender], total_enrollment),
                'order': GENDER_ORDER[gender]
            })

        return sorted(recent_genders, key=lambda i: i['order'], reverse=False)

    def _build_gender_known_percent(self, api_response):
        most_recent_data = api_response[-1]
        known_enrollment = self._calculate_sum(most_recent_data, KNOWN_GENDERS)
        all_enrollment = self._calculate_sum(most_recent_data, GENDERS)
        return utils.math.calculate_percent(known_enrollment, all_enrollment)

    def get_ages(self):
        """
        Returns the updated time, summary of age ranges displayed in metrics, and
        ages with counts and percentages and ages greater than MAX_AGE aggregated
        within MAX_AGE.
        """
        api_response = self.course.enrollment(demographic.BIRTH_YEAR)
        last_updated = None
        binned_ages = None
        summary = None
        known_enrollment_percent = None

        if api_response:
            last_updated = self.parse_api_datetime(api_response[0]['created'])
            api_response = sorted(api_response, key=lambda i: i['birth_year'], reverse=True)
            summary = self._build_ages_summary(api_response)
            binned_ages = self._build_binned_ages(api_response)
            known_enrollment_percent = self._calculate_known_total_percent(api_response, 'birth_year')

        return last_updated, summary, binned_ages, known_enrollment_percent

    def _count_ages(self, api_response, min_age, max_age):
        """
        Returns the number of enrollments between min_age (exclusive) and
        max_age (inclusive).
        """
        current_year = datetime.date.today().year
        filtered_ages = api_response

        if min_age:
            filtered_ages = ([datum for datum in filtered_ages
                              if datum['birth_year'] and (current_year - datum['birth_year']) > min_age])
        if max_age:
            filtered_ages = ([datum for datum in filtered_ages
                              if datum['birth_year'] and (current_year - datum['birth_year']) <= max_age])
        return self.sum_counts(filtered_ages)

    def _calculate_median_age(self, api_response):
        current_year = datetime.date.today().year
        total_enrollment = self.sum_counts(api_response)
        half_enrollments = total_enrollment * 0.5
        count_enrollments = 0
        for index, datum in enumerate(api_response):
            age = current_year - datum['birth_year']
            count_enrollments += datum['count']

            if count_enrollments > half_enrollments:
                return age
            elif count_enrollments == half_enrollments:
                if total_enrollment % 2 == 0:
                    # When no single median value, calculate the mean between the flanking ages.  It will always
                    # be the case that at the loop can be advanced
                    next_age = current_year - api_response[index + 1]['birth_year']
                    return (next_age + age) * 0.5
                else:
                    return age

        return None

    def _build_ages_summary(self, api_response):
        """ Returns age metrics, excluding unknown ages. """
        known_ages = [i for i in api_response if i['birth_year']]
        summary = {'median': self._calculate_median_age(known_ages)}

        summary_params = [
            {
                'field': 'under_25',
                'ages': [None, 25]
            },
            {
                'field': 'between_26_40',
                'ages': [26, 40]
            },
            {
                'field': 'over_40',
                'ages': [40, None]
            }
        ]

        # calculate the percentages for each age range
        known_enrollment_total = self._calculate_known_total_enrollment(api_response, 'birth_year')
        for params in summary_params:
            age_range = params['ages']
            count = self._count_ages(api_response, age_range[0], age_range[1])
            summary[params['field']] = utils.math.calculate_percent(count, known_enrollment_total)

        return summary

    def _build_binned_ages(self, api_response):
        current_year = datetime.date.today().year
        known_ages = [i for i in api_response if i['birth_year']]
        enrollment_total = self.sum_counts(api_response)

        binned_ages = [{'age': current_year - int(datum['birth_year']),
                        'count': datum['count'],
                        'percent': utils.math.calculate_percent(datum['count'], enrollment_total)}
                       for datum in known_ages]

        # fill in ages with no counts for display
        for age in range(self.MAX_AGE + 1):
            try:
                binned = next(binned for binned in binned_ages if binned['age'] is age)
            except StopIteration:
                binned = None
            if not binned:
                binned = {'age': age, 'count': 0, 'percent': 0}
                binned_ages.append(binned)

        # fill in gaps may have altered the ordering
        binned_ages = sorted(binned_ages, key=lambda i: i['age'], reverse=False)

        # bin all the ages above MAX_AGE (e.g. 100) and remove them from the dataset
        elderly = [datum for datum in binned_ages if datum['age'] > self.MAX_AGE]
        elderly_bin = next(binned for binned in binned_ages if binned['age'] is self.MAX_AGE)
        for datum in elderly:
            elderly_bin['count'] = elderly_bin['count'] + datum['count']
            binned_ages.remove(datum)
        elderly_bin['percent'] = utils.math.calculate_percent(elderly_bin['count'], enrollment_total)

        # tack enrollment counts for students with unknown ages
        unknown = [i for i in api_response if not i['birth_year']]
        if unknown:
            unknown_count = unknown[0]['count']
            binned_ages.append({
                'age': _('Unknown'),
                'count': unknown_count,
                'percent': utils.math.calculate_percent(unknown_count, enrollment_total)
            })

        return binned_ages

    def _calculate_sum(self, dictionary, keys):
        """ Returns the sum of the values from the keys specified. """
        return sum([value for key, value in dictionary.iteritems() if value and key in keys])

    def _calculate_known_total_enrollment(self, api_response, enrollment_key):
        known = [i for i in api_response if i[enrollment_key]]
        return self.sum_counts(known)

    def _calculate_known_total_percent(self, api_response, enrollment_key):
        known_count = self._calculate_known_total_enrollment(api_response, enrollment_key)
        total_count = self.sum_counts(api_response)
        return utils.math.calculate_percent(known_count, total_count)

    def _calculate_education_percent(self, api_response, levels):
        """ Aggregates levels of education and returns the percent of the total. """
        filtered_levels = ([education for education in api_response
                            if education['education_level'] in levels])
        subset_enrollment = self.sum_counts(filtered_levels)
        return utils.math.calculate_percent(subset_enrollment, self.sum_counts(api_response))

    def _build_education_summary(self, api_response):
        known_education = [i for i in api_response if i['education_level']]

        high_school_or_less = [EDUCATION_LEVEL.PRIMARY, EDUCATION_LEVEL.JUNIOR_SECONDARY,
                               EDUCATION_LEVEL.SECONDARY]
        college_levels = [EDUCATION_LEVEL.ASSOCIATES, EDUCATION_LEVEL.BACHELORS]
        advanced_levels = [EDUCATION_LEVEL.MASTERS, EDUCATION_LEVEL.DOCTORATE]
        return {
            'high_school_or_less': self._calculate_education_percent(known_education,
                                                                     high_school_or_less),
            'college': self._calculate_education_percent(known_education, college_levels),
            'advanced': self._calculate_education_percent(known_education, advanced_levels),
        }

    def _build_education_levels(self, api_response):
        known_education = [i for i in api_response if i['education_level']]
        known_enrollment_total = self.sum_counts(known_education)
        levels = [{'educationLevel': EDUCATION_NAMES[datum['education_level']],
                   'count': datum['count'],
                   'percent': utils.math.calculate_percent(datum['count'], known_enrollment_total),
                   'order': EDUCATION_ORDER[datum['education_level']]}
                  for datum in known_education]

        levels = sorted(levels, key=lambda i: i['order'], reverse=False)

        # add unknown (not reported) education levels if available
        unknown = [i for i in api_response if not i['education_level']]
        if unknown:
            unknown_count = unknown[0]['count']
            levels.append({
                'educationLevel': UNKNOWN_EDUCATION_LEVEL_NAME,
                'count': unknown_count
            })

        return levels

    def _fill_empty_education_levels(self, api_response):
        found_levels = [level['education_level'] for level in api_response]
        # get the symmetric difference
        missed_levels = list(set(found_levels) ^ set(KNOWN_EDUCATION_LEVELS))

        for level in missed_levels:
            api_response.append({
                'education_level': level,
                'count': 0
            })

        return api_response

    def get_education(self):
        api_response = self.course.enrollment(demographic.EDUCATION)
        education_levels = None
        education_summary = None
        last_updated = None
        known_enrollment_percent = None

        if api_response:
            last_updated = self.parse_api_datetime(api_response[0]['created'])
            api_response = self._fill_empty_education_levels(api_response)
            education_levels = self._build_education_levels(api_response)
            education_summary = self._build_education_summary(api_response)
            known_enrollment_percent = self._calculate_known_total_percent(api_response, 'education_level')

        return last_updated, education_summary, education_levels, known_enrollment_percent
