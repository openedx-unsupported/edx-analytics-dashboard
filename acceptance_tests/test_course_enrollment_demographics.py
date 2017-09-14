import datetime

from analyticsclient.constants import demographic
import analyticsclient.constants.education_level as EDUCATION_LEVEL
import analyticsclient.constants.gender as GENDER
from bok_choy.web_app_test import WebAppTest

from acceptance_tests.mixins import CourseDemographicsPageTestsMixin
from acceptance_tests.pages import CourseEnrollmentDemographicsAgePage, CourseEnrollmentDemographicsEducationPage, \
    CourseEnrollmentDemographicsGenderPage


_multiprocess_can_split_ = True


class CourseEnrollmentDemographicsAgeTests(CourseDemographicsPageTestsMixin, WebAppTest):
    help_path = 'enrollment/Demographics_Age.html'

    demographic_type = demographic.BIRTH_YEAR
    table_columns = ['Age', 'Number of Learners', 'Percent of Total']

    def setUp(self):
        super(CourseEnrollmentDemographicsAgeTests, self).setUp()
        self.page = CourseEnrollmentDemographicsAgePage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)

        self.demographic_data = sorted(self.course.enrollment(self.demographic_type),
                                       key=lambda item: item['count'], reverse=True)

        # Remove items with no birth year
        self.demographic_data_without_none = [datum for datum in self.demographic_data if datum['birth_year']]

    def test_page(self):
        super(CourseEnrollmentDemographicsAgeTests, self).test_page()
        self._test_metrics()

    def _calculate_median_age(self, current_year):
        demographic_data = self.demographic_data_without_none

        total_enrollment = sum([datum['count'] for datum in demographic_data])
        half_enrollments = total_enrollment * 0.5
        count_enrollments = 0

        data = sorted(demographic_data, key=lambda item: item['birth_year'], reverse=False)

        for index, datum in enumerate(data):
            age = current_year - datum['birth_year']
            count_enrollments += datum['count']

            if count_enrollments > half_enrollments:
                return age
            elif count_enrollments == half_enrollments:
                if total_enrollment % 2 == 0:
                    next_age = current_year - data[index + 1]['birth_year']
                    return (next_age + age) * 0.5
                return age

        return None

    def _count_ages(self, current_year, min_age, max_age):
        """
        Returns the number of enrollments between min_age (inclusive) and
        max_age (exclusive).
        """
        filtered_ages = self.demographic_data_without_none

        if min_age:
            filtered_ages = ([datum for datum in filtered_ages
                              if (current_year - datum['birth_year']) >= min_age])
        if max_age:
            filtered_ages = ([datum for datum in filtered_ages
                              if (current_year - datum['birth_year']) < max_age])

        return sum([datum['count'] for datum in filtered_ages])

    def _test_metrics(self):
        current_year = datetime.date.today().year
        total = float(sum([datum['count'] for datum in self.demographic_data_without_none]))
        age_metrics = [
            {
                'stat_type': 'median_age',
                'value': self._calculate_median_age(current_year)
            },
            {
                'stat_type': 'enrollment_age_under_25',
                'value': self.build_display_percentage(self._count_ages(current_year, None, 26), total)
            },
            {
                'stat_type': 'enrollment_age_between_26_40',
                'value': self.build_display_percentage(self._count_ages(current_year, 26, 41), total)
            },
            {
                'stat_type': 'enrollment_age_over_40',
                'value': self.build_display_percentage(self._count_ages(current_year, 41, None), total)
            }
        ]

        for metric in age_metrics:
            selector = 'data-stat-type={}'.format(metric['stat_type'])
            self.assertSummaryPointValueEquals(selector, unicode(metric['value']))

    def _test_table_row(self, datum, column, sum_count):
        expected_percent_display = self.build_display_percentage(datum['count'], sum_count)
        # it's difficult to test the actual age in the case of a tie, so leave out (unit tests should catch this)
        expected = [self.format_number(datum['count']), expected_percent_display]
        actual = [column[1].text, column[2].text]
        self.assertListEqual(actual, expected)
        self.assertIn('text-right', column[1].get_attribute('class'))
        self.assertIn('text-right', column[2].get_attribute('class'))


class CourseEnrollmentDemographicsGenderTests(CourseDemographicsPageTestsMixin, WebAppTest):
    help_path = 'enrollment/Demographics_Gender.html'

    demographic_type = demographic.GENDER
    table_columns = ['Date', 'Current Enrollment', 'Female', 'Male', 'Other', 'Not Reported']

    def setUp(self):
        super(CourseEnrollmentDemographicsGenderTests, self).setUp()
        self.page = CourseEnrollmentDemographicsGenderPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)

        end_date = datetime.datetime.utcnow()
        end_date_string = end_date.strftime(self.analytics_api_client.DATETIME_FORMAT)
        response = self.course.enrollment(self.demographic_type, end_date=end_date_string)
        self.demographic_data = sorted(response, key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'),
                                       reverse=True)

    def _test_table_row(self, datum, column, sum_count):
        genders = [GENDER.FEMALE, GENDER.MALE, GENDER.OTHER, GENDER.UNKNOWN]
        expected_date = datetime.datetime.strptime(datum['date'], self.api_date_format).strftime("%B %d, %Y")
        expected_date = self.date_strip_leading_zeroes(expected_date)
        gender_total = sum([value for key, value in datum.iteritems() if value and key in genders])

        expected = [expected_date, self.format_number(gender_total)]
        for gender in genders:
            expected.append(self.format_number(datum.get(gender, 0) or 0))

        actual = []
        for i in range(6):
            actual.append(column[i].text)

        self.assertListEqual(actual, expected)

        for i in range(1, 6):
            self.assertIn('text-right', column[i].get_attribute('class'))


class CourseEnrollmentDemographicsEducationTests(CourseDemographicsPageTestsMixin, WebAppTest):
    EDUCATION_NAMES = {
        EDUCATION_LEVEL.NONE: 'None',
        EDUCATION_LEVEL.OTHER: 'Other',
        EDUCATION_LEVEL.PRIMARY: 'Primary',
        EDUCATION_LEVEL.JUNIOR_SECONDARY: 'Middle',
        EDUCATION_LEVEL.SECONDARY: 'Secondary',
        EDUCATION_LEVEL.ASSOCIATES: 'Associate',
        EDUCATION_LEVEL.BACHELORS: "Bachelor's",
        EDUCATION_LEVEL.MASTERS: "Master's",
        EDUCATION_LEVEL.DOCTORATE: 'Doctorate',
        None: 'Unknown'
    }

    help_path = 'enrollment/Demographics_Education.html'

    demographic_type = demographic.EDUCATION
    table_columns = ['Educational Background', 'Number of Learners']

    def setUp(self):
        super(CourseEnrollmentDemographicsEducationTests, self).setUp()
        self.page = CourseEnrollmentDemographicsEducationPage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)
        self.demographic_data = sorted(self.course.enrollment(self.demographic_type),
                                       key=lambda item: item['count'], reverse=True)

    def test_page(self):
        super(CourseEnrollmentDemographicsEducationTests, self).test_page()
        self._test_metrics()

    def _test_metrics(self):
        # The total should not include users who did not provide an education level
        total = sum([datum['count'] for datum in self.demographic_data if datum['education_level']])

        education_groups = [
            {
                'levels': ['primary', 'junior_secondary', 'secondary'],
                'stat_type': 'education_high_school_or_less_enrollment',
                'tooltip': 'The percentage of learners who selected Secondary/high school, Junior secondary/junior '
                           'high/middle school, or Elementary/primary school as their highest level of '
                           'education completed.'
            },
            {
                'levels': ['associates', 'bachelors'],
                'stat_type': 'education_college_enrollment',
                'tooltip': "The percentage of learners who selected Bachelor's degree or Associate degree as their "
                           "highest level of education completed."
            },
            {
                'levels': ['masters', 'doctorate'],
                'stat_type': 'education_advanced_enrollment',
                'tooltip': "The percentage of learners who selected Doctorate or Master's or professional degree as "
                           "their highest level of education completed."
            }
        ]

        for group in education_groups:
            selector = 'data-stat-type={}'.format(group['stat_type'])
            filtered_group = ([education for education in self.demographic_data
                               if education['education_level'] in group['levels']])
            group_total = float(sum([datum['count'] for datum in filtered_group]))
            expected_percent_display = self.build_display_percentage(group_total, total)
            self.assertSummaryPointValueEquals(selector, expected_percent_display)
            self.assertSummaryTooltipEquals(selector, group['tooltip'])

    def _test_table_row(self, datum, column, sum_count):
        expected = [self.EDUCATION_NAMES[datum['education_level']], self.format_number(datum['count'])]
        actual = [column[0].text, column[1].text]
        self.assertListEqual(actual, expected)
        self.assertIn('text-right', column[1].get_attribute('class'))
