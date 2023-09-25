import logging

from analyticsclient.exceptions import NotFoundError
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop

from analytics_dashboard.core.utils import translate_dict_values
from analytics_dashboard.courses.presenters.enrollment import (
    CourseEnrollmentDemographicsPresenter,
    CourseEnrollmentPresenter,
)
from analytics_dashboard.courses.views import CourseTemplateWithNavView, AnalyticsV0Mixin, AnalyticsV1Mixin
from analytics_dashboard.courses.waffle import age_available

logger = logging.getLogger(__name__)


# separated from EnrollmentTemplateView so it can be rerun in test
def _enrollment_secondary_nav():
    demographics_landing_view = {
        'name': 'demographics',
        'text': gettext_noop('Demographics'),
        'view': 'courses:enrollment:demographics_age',
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'demographics',
        'depth': 'age'
    } if age_available() else {
        'name': 'demographics',
        'text': gettext_noop('Demographics'),
        'view': 'courses:enrollment:demographics_education',
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'demographics',
        'depth': 'education'
    }

    secondary_nav_items = [
        {
            'name': 'activity',
            'text': gettext_noop('Activity'),
            'view': 'courses:enrollment:activity',
            'scope': 'course',
            'lens': 'enrollment',
            'report': 'activity',
            'depth': ''
        },
        demographics_landing_view,
        {
            'name': 'geography',
            'text': gettext_noop('Geography'),
            'view': 'courses:enrollment:geography',
            'scope': 'course',
            'lens': 'enrollment',
            'report': 'geography',
            'depth': ''
        },
    ]
    translate_dict_values(secondary_nav_items, ('text',))
    return secondary_nav_items


class EnrollmentTemplateView(CourseTemplateWithNavView):
    """
    Base view for course enrollment pages.
    """
    secondary_nav_items = _enrollment_secondary_nav()
    active_primary_nav_item = 'enrollment'


# separated from the class so it can be invoked in test with varying settings
def _enrollment_tertiary_nav():
    tertiary_age = [
        {
            'name': 'age',
            'text': gettext_noop('Age'),
            'view': 'courses:enrollment:demographics_age',
            'scope': 'course',
            'lens': 'enrollment',
            'report': 'demographics',
            'depth': 'age'
        }
    ] if age_available() else []
    tertiary_nav_items = tertiary_age + [
        {
            'name': 'education',
            'text': gettext_noop('Education'),
            'view': 'courses:enrollment:demographics_education',
            'scope': 'course',
            'lens': 'enrollment',
            'report': 'demographics',
            'depth': 'education'
        },
        {
            'name': 'gender',
            'text': gettext_noop('Gender'),
            'view': 'courses:enrollment:demographics_gender',
            'scope': 'course',
            'lens': 'enrollment',
            'report': 'demographics',
            'depth': 'gender'
        }
    ]
    translate_dict_values(tertiary_nav_items, ('text',))
    return tertiary_nav_items


class EnrollmentDemographicsTemplateView(EnrollmentTemplateView):
    """
    Base view for course enrollment demographics pages.
    """
    active_secondary_nav_item = 'demographics'

    tertiary_nav_items = _enrollment_tertiary_nav()

    # Translators: Do not translate UTC.
    update_message = _('Demographic learner data was last updated %(update_date)s at %(update_time)s UTC.')

    # Translators: This sentence is displayed at the bottom of the page and describe the demographics data displayed.
    data_information_message = _('All above demographic data was self-reported at the time of registration.')

    def format_percentage(self, value):
        if value is None:
            formatted_percent = '0'
        else:
            formatted_percent = intcomma(round(value, 3) * 100)

        return formatted_percent


class EnrollmentActivityView(AnalyticsV1Mixin, EnrollmentTemplateView):
    template_name = 'courses/enrollment_activity.html'
    page_title = _('Enrollment Activity')
    page_name = {
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'activity',
        'depth': ''
    }
    active_secondary_nav_item = 'activity'

    # Translators: Do not translate UTC.
    update_message = _('Enrollment activity data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        presenter = CourseEnrollmentPresenter(self.course_id, self.analytics_client)

        summary = None
        trend = None
        last_updated = None
        try:
            summary, trend = presenter.get_summary_and_trend_data()
            last_updated = summary['last_updated']
        except NotFoundError:
            logger.error("Failed to retrieve enrollment activity data for %s.", self.course_id)

        # add the enrollment data for the page
        context['js_data']['course']['enrollmentTrends'] = trend

        context.update({
            'summary': summary,
            'update_message': self.get_last_updated_message(last_updated)
        })
        context['page_data'] = self.get_page_data(context)

        return context


class EnrollmentDemographicsAgeView(AnalyticsV0Mixin, EnrollmentDemographicsTemplateView):
    template_name = 'courses/enrollment_demographics_age.html'
    page_title = _('Enrollment Demographics by Age')
    page_name = {
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'demographics',
        'depth': 'age'
    }
    active_tertiary_nav_item = 'age'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = CourseEnrollmentDemographicsPresenter(self.course_id, self.analytics_client)
        binned_ages = None
        summary = None
        known_enrollment_percent = None
        last_updated = None

        try:
            last_updated, summary, binned_ages, known_enrollment_percent = presenter.get_ages()
        except NotFoundError:
            logger.error("Failed to retrieve enrollment demographic age data for %s.", self.course_id)

        # add the enrollment data for the page
        context['js_data']['course']['ages'] = binned_ages

        context.update({
            'summary': summary,
            'chart_tooltip_value': self.format_percentage(known_enrollment_percent),
            'update_message': self.get_last_updated_message(last_updated),
            'data_information_message': self.data_information_message
        })
        context['page_data'] = self.get_page_data(context)

        return context


class EnrollmentDemographicsEducationView(AnalyticsV1Mixin, EnrollmentDemographicsTemplateView):
    template_name = 'courses/enrollment_demographics_education.html'
    page_title = _('Enrollment Demographics by Education')
    page_name = {
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'demographics',
        'depth': 'education'
    }
    active_tertiary_nav_item = 'education'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = CourseEnrollmentDemographicsPresenter(self.course_id, self.analytics_client)
        binned_education = None
        summary = None
        known_enrollment_percent = None
        last_updated = None

        try:
            last_updated, summary, binned_education, known_enrollment_percent = presenter.get_education()
        except NotFoundError:
            logger.error("Failed to retrieve enrollment demographic education data for %s.", self.course_id)

        # add the enrollment data for the page
        context['js_data']['course']['education'] = binned_education

        context.update({
            'summary': summary,
            'chart_tooltip_value': self.format_percentage(known_enrollment_percent),
            'update_message': self.get_last_updated_message(last_updated),
            'data_information_message': self.data_information_message
        })
        context['page_data'] = self.get_page_data(context)

        return context


class EnrollmentDemographicsGenderView(AnalyticsV1Mixin, EnrollmentDemographicsTemplateView):
    template_name = 'courses/enrollment_demographics_gender.html'
    page_title = _('Enrollment Demographics by Gender')
    page_name = {
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'demographics',
        'depth': 'gender'
    }
    active_tertiary_nav_item = 'gender'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = CourseEnrollmentDemographicsPresenter(self.course_id, self.analytics_client)
        gender_data = None
        trend = None
        known_enrollment_percent = None
        last_updated = None

        try:
            last_updated, gender_data, trend, known_enrollment_percent = presenter.get_gender()
        except NotFoundError:
            logger.error("Failed to retrieve enrollment demographic gender data for %s.", self.course_id)

        # add the enrollment data for the page
        context['js_data']['course']['genders'] = gender_data
        context['js_data']['course']['genderTrend'] = trend

        context.update({
            'update_message': self.get_last_updated_message(last_updated),
            'chart_tooltip_value': self.format_percentage(known_enrollment_percent),
            'data_information_message': self.data_information_message
        })
        context['page_data'] = self.get_page_data(context)

        return context


class EnrollmentGeographyView(AnalyticsV1Mixin, EnrollmentTemplateView):
    template_name = 'courses/enrollment_geography.html'
    page_title = _('Enrollment Geography')
    page_name = {
        'scope': 'course',
        'lens': 'enrollment',
        'report': 'geography',
        'depth': ''
    }
    active_secondary_nav_item = 'geography'

    # Translators: Do not translate UTC.
    update_message = _('Geographic learner data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        presenter = CourseEnrollmentPresenter(self.course_id, self.analytics_client)

        data = None
        last_updated = None
        try:
            summary, data = presenter.get_geography_data()
            last_updated = summary['last_updated']

            # Add summary data (e.g. num countries, top 3 countries) directly to the context
            context.update(summary)
        except NotFoundError:
            logger.error("Failed to retrieve enrollment geography data for %s.", self.course_id)

        context['js_data']['course']['enrollmentByCountry'] = data

        context.update({
            'update_message': self.get_last_updated_message(last_updated)
        })
        context['page_data'] = self.get_page_data(context)

        return context
