import json

import mock
from ddt import ddt
from django.test import TestCase

from courses.tests.test_views import CourseEnrollmentDemographicsMixin, CourseEnrollmentViewTestMixin
from courses.tests import utils


@ddt
class CourseEnrollmentActivityViewTests(CourseEnrollmentViewTestMixin, TestCase):
    viewname = 'courses:enrollment:activity'
    active_secondary_nav_label = 'Activity'
    presenter_method = 'courses.presenters.enrollment.CourseEnrollmentPresenter.get_summary_and_trend_data'

    def assertViewIsValid(self, course_id):
        summary, enrollment_data = utils.get_mock_enrollment_summary_and_trend(course_id)
        rv = summary, enrollment_data
        with mock.patch(self.presenter_method, return_value=rv):
            response = self.client.get(self.path(course_id=course_id))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        # check page title
        self.assertEqual(context['page_title'], 'Enrollment Activity')

        # make sure the summary numbers are correct
        self.assertDictEqual(context['summary'], summary)

        # make sure the trend is correct
        page_data = json.loads(context['page_data'])
        trend_data = page_data['course']['enrollmentTrends']
        expected = enrollment_data
        self.assertListEqual(trend_data, expected)

        self.assertPrimaryNav(context['primary_nav_item'], course_id)
        self.assertSecondaryNavs(context['secondary_nav_items'], course_id)
        self.assertValidCourseName(course_id, response.context)

    def assertValidMissingDataContext(self, context):
        self.assertIsNone(context['summary'])
        self.assertIsNone(context['js_data']['course']['enrollmentTrends'])


@ddt
class CourseEnrollmentGeographyViewTests(CourseEnrollmentViewTestMixin, TestCase):
    viewname = 'courses:enrollment:geography'
    active_secondary_nav_label = 'Geography'
    presenter_method = 'courses.presenters.enrollment.CourseEnrollmentPresenter.get_geography_data'

    def get_mock_data(self, course_id):
        return utils.get_mock_api_enrollment_geography_data(course_id)

    def assertViewIsValid(self, course_id):
        with mock.patch(self.presenter_method, return_value=utils.get_mock_presenter_enrollment_geography_data()):
            response = self.client.get(self.path(course_id=course_id))
            context = response.context

            # make sure that we get a 200
            self.assertEqual(response.status_code, 200)

            # check page title
            self.assertEqual(context['page_title'], 'Enrollment Geography')

            page_data = json.loads(context['page_data'])
            _summary, expected_data = utils.get_mock_presenter_enrollment_geography_data()
            self.assertEqual(page_data['course']['enrollmentByCountry'], expected_data)

            self.assertValidCourseName(course_id, response.context)

    def assertValidMissingDataContext(self, context):
        self.assertIsNone(context['update_message'])
        self.assertIsNone(context['js_data']['course']['enrollmentByCountry'])


@ddt
class CourseEnrollmentDemographicsAge(CourseEnrollmentDemographicsMixin, TestCase):
    viewname = 'courses:enrollment:demographics_age'
    active_tertiary_nav_label = 'Age'
    presenter_method = 'courses.presenters.enrollment.CourseEnrollmentDemographicsPresenter.get_ages'

    def assertViewIsValid(self, course_id):
        last_updated, summary, binned_ages, known_percent = utils.get_presenter_ages()
        rv = last_updated, summary, binned_ages, known_percent
        with mock.patch(self.presenter_method, return_value=rv):
            response = self.client.get(self.path(course_id=course_id))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        # check page title
        self.assertEqual(context['page_title'], 'Enrollment Demographics by Age')

        self.assertEqual(context['chart_tooltip_value'], self.format_tip_percent(known_percent))

        page_data = json.loads(context['page_data'])
        actual_ages = page_data['course']['ages']
        self.assertListEqual(actual_ages, binned_ages)
        self.assertDictEqual(context['summary'], summary)
        self.assertAllNavs(context, course_id)

        self.assertValidCourseName(course_id, response.context)

    def get_mock_data(self, course_id):
        return utils.get_mock_api_enrollment_age_data(course_id)

    def assertValidMissingDataContext(self, context):
        self.assertIsNone(context['js_data']['course']['ages'])
        self.assertIsNone(context['summary'])


@ddt
class CourseEnrollmentDemographicsEducation(CourseEnrollmentDemographicsMixin, TestCase):
    viewname = 'courses:enrollment:demographics_education'
    active_tertiary_nav_label = 'Education'
    presenter_method = 'courses.presenters.enrollment.CourseEnrollmentDemographicsPresenter.get_education'

    def assertViewIsValid(self, course_id):
        last_updated, summary, education_data, known_percent = utils.get_presenter_education()
        rv = last_updated, summary, education_data, known_percent
        with mock.patch(self.presenter_method, return_value=rv):
            response = self.client.get(self.path(course_id=course_id))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        # check page title
        self.assertEqual(context['page_title'], 'Enrollment Demographics by Education')

        self.assertEqual(context['chart_tooltip_value'], self.format_tip_percent(known_percent))

        page_data = json.loads(context['page_data'])
        actual_education = page_data['course']['education']
        self.assertListEqual(actual_education, education_data)
        self.assertDictEqual(context['summary'], summary)
        self.assertAllNavs(context, course_id)

        self.assertValidCourseName(course_id, response.context)

    def get_mock_data(self, course_id):
        return utils.get_mock_api_enrollment_education_data(course_id)

    def assertValidMissingDataContext(self, context):
        self.assertIsNone(context['js_data']['course']['education'])
        self.assertIsNone(context['summary'])


@ddt
class CourseEnrollmentDemographicsGender(CourseEnrollmentDemographicsMixin, TestCase):
    viewname = 'courses:enrollment:demographics_gender'
    active_tertiary_nav_label = 'Gender'
    presenter_method = 'courses.presenters.enrollment.CourseEnrollmentDemographicsPresenter.get_gender'

    def assertViewIsValid(self, course_id):
        last_updated, gender_data, trend, known_percent = utils.get_presenter_gender(course_id)
        rv = last_updated, gender_data, trend, known_percent
        with mock.patch(self.presenter_method, return_value=rv):
            response = self.client.get(self.path(course_id=course_id))

        context = response.context

        # Ensure we get a valid HTTP status
        self.assertEqual(response.status_code, 200)

        # check page title
        self.assertEqual(context['page_title'], 'Enrollment Demographics by Gender')

        self.assertEqual(context['chart_tooltip_value'], self.format_tip_percent(known_percent))

        page_data = json.loads(context['page_data'])
        actual_genders = page_data['course']['genders']
        self.assertListEqual(actual_genders, gender_data)

        actual_trends = page_data['course']['genderTrend']
        self.assertListEqual(actual_trends, trend)

        self.assertAllNavs(context, course_id)
        self.assertValidCourseName(course_id, response.context)

    def get_mock_data(self, course_id):
        return utils.get_mock_api_enrollment_gender_data(course_id)

    def assertValidMissingDataContext(self, context):
        self.assertIsNone(context['js_data']['course']['genders'])
        self.assertIsNone(context['js_data']['course']['genderTrend'])
