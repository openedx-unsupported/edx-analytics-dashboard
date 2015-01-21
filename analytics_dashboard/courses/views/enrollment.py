import logging

from django.contrib.humanize.templatetags.humanize import intcomma

from django.utils.translation import ugettext_lazy as _
from analyticsclient.exceptions import NotFoundError

from courses.presenters.enrollment import CourseEnrollmentPresenter, CourseEnrollmentDemographicsPresenter
from courses.views import CourseTemplateWithNavView


logger = logging.getLogger(__name__)


class EnrollmentTemplateView(CourseTemplateWithNavView):
    """
    Base view for course enrollment pages.
    """
    secondary_nav_items = [
        {'name': 'activity', 'label': _('Activity'), 'view': 'courses:enrollment:activity'},
        {'name': 'demographics', 'label': _('Demographics'), 'view': 'courses:enrollment:demographics_age'},
        {'name': 'geography', 'label': _('Geography'), 'view': 'courses:enrollment:geography'},
    ]
    active_primary_nav_item = 'enrollment'


class EnrollmentDemographicsTemplateView(EnrollmentTemplateView):
    """
    Base view for course enrollment demographics pages.
    """
    active_secondary_nav_item = 'demographics'
    tertiary_nav_items = [
        {'name': 'age', 'label': _('Age'), 'view': 'courses:enrollment:demographics_age'},
        {'name': 'education', 'label': _('Education'), 'view': 'courses:enrollment:demographics_education'},
        {'name': 'gender', 'label': _('Gender'), 'view': 'courses:enrollment:demographics_gender'}
    ]

    # Translators: Do not translate UTC.
    update_message = _('Demographic student data was last updated %(update_date)s at %(update_time)s UTC.')

    # pylint: disable=line-too-long
    # Translators: This sentence is displayed at the bottom of the page and describe the demographics data displayed.
    data_information_message = _('All above demographic data was self-reported at the time of registration.')

    def format_percentage(self, value):
        if value is None:
            formatted_percent = u'0'
        else:
            formatted_percent = intcomma(round(value, 3) * 100)

        return formatted_percent


class EnrollmentActivityView(EnrollmentTemplateView):
    template_name = 'courses/enrollment_activity.html'
    page_title = _('Enrollment Activity')
    page_name = 'enrollment_activity'
    active_secondary_nav_item = 'activity'

    # Translators: Do not translate UTC.
    update_message = _('Enrollment activity data was last updated %(update_date)s at %(update_time)s UTC.')

    # pylint: disable=line-too-long
    def get_context_data(self, **kwargs):
        context = super(EnrollmentActivityView, self).get_context_data(**kwargs)

        presenter = CourseEnrollmentPresenter(self.course_id)

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


class EnrollmentDemographicsAgeView(EnrollmentDemographicsTemplateView):
    template_name = 'courses/enrollment_demographics_age.html'
    page_title = _('Enrollment Demographics by Age')
    page_name = 'enrollment_demographics_age'
    active_tertiary_nav_item = 'age'

    def get_context_data(self, **kwargs):
        context = super(EnrollmentDemographicsAgeView, self).get_context_data(**kwargs)
        presenter = CourseEnrollmentDemographicsPresenter(self.course_id)
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


class EnrollmentDemographicsEducationView(EnrollmentDemographicsTemplateView):
    template_name = 'courses/enrollment_demographics_education.html'
    page_title = _('Enrollment Demographics by Education')
    page_name = 'enrollment_demographics_education'
    active_tertiary_nav_item = 'education'

    def get_context_data(self, **kwargs):
        context = super(EnrollmentDemographicsEducationView, self).get_context_data(**kwargs)
        presenter = CourseEnrollmentDemographicsPresenter(self.course_id)
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


class EnrollmentDemographicsGenderView(EnrollmentDemographicsTemplateView):
    template_name = 'courses/enrollment_demographics_gender.html'
    page_title = _('Enrollment Demographics by Gender')
    page_name = 'enrollment_demographics_gender'
    active_tertiary_nav_item = 'gender'

    def get_context_data(self, **kwargs):
        context = super(EnrollmentDemographicsGenderView, self).get_context_data(**kwargs)
        presenter = CourseEnrollmentDemographicsPresenter(self.course_id)
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


class EnrollmentGeographyView(EnrollmentTemplateView):
    template_name = 'courses/enrollment_geography.html'
    page_title = _('Enrollment Geography')
    page_name = 'enrollment_geography'
    active_secondary_nav_item = 'geography'

    # Translators: Do not translate UTC.
    update_message = _('Geographic student data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super(EnrollmentGeographyView, self).get_context_data(**kwargs)

        presenter = CourseEnrollmentPresenter(self.course_id)

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
