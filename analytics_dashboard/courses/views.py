import copy
import datetime
import json
import logging
import re
import urllib

from django.contrib.humanize.templatetags.humanize import intcomma
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils import dateformat
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _
from braces.views import LoginRequiredMixin
import requests
from waffle import switch_is_active
from analyticsclient.constants import data_format, demographic
from analyticsclient.client import Client
from analyticsclient.exceptions import NotFoundError

from courses import permissions
from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter, \
    CourseEnrollmentDemographicsPresenter
from courses.serializers import LazyEncoder
from courses.utils import is_feature_enabled
from help.views import ContextSensitiveHelpMixin


logger = logging.getLogger(__name__)


class TrackedViewMixin(object):
    """
    Adds tracking variables to the context passed to Javascript.
    """

    # Page name used for usage tracking/analytics
    page_name = None

    def get_context_data(self, **kwargs):
        context = super(TrackedViewMixin, self).get_context_data(**kwargs)
        context['js_data'] = context.get('js_data', {})
        context['js_data'].update({
            'tracking': {
                'segmentApplicationId': settings.SEGMENT_IO_KEY,  # None will translate to 'null'
                'page': self.page_name
            }
        })
        return context


class LazyEncoderMixin(object):
    def get_page_data(self, context):
        """ Returns JSON serialized data with lazy translations converted. """
        if 'js_data' in context:
            return json.dumps(context['js_data'], cls=LazyEncoder)
        else:
            return None


class CourseContextMixin(TrackedViewMixin, LazyEncoderMixin):
    """
    Adds default course context data.

    Use primarily with templated views where data needs to be passed to Javascript.
    """
    # Title displayed on the page
    page_title = None
    page_subtitle = None

    def _ignore_in_reporting(self, user):
        if settings.SEGMENT_IGNORE_EMAIL_REGEX:
            return bool(re.match(settings.SEGMENT_IGNORE_EMAIL_REGEX, user.email))

        return False

    def get_context_data(self, **kwargs):
        context = super(CourseContextMixin, self).get_context_data(**kwargs)
        context.update(self.get_default_data())

        user = self.request.user
        context['js_data'] = context.get('js_data', {})
        context['js_data'].update({
            'course': {
                'courseId': self.course_id
            },
            'user': {
                'userId': user.get_username(),
                'userName': user.get_full_name(),
                'userEmail': user.email,
                'ignoreInReporting': self._ignore_in_reporting(user)
            },
        })

        return context

    def get_default_data(self):
        """
        Returns default data for the pages (context and javascript data).
        """
        context = {
            'course_id': self.course_id,
            'course_key': self.course_key,
            'page_title': self.page_title,
            'page_subtitle': self.page_subtitle
        }

        return context


class CourseValidMixin(object):
    """
    Mixin that checks the validity of a course ID against the LMS.
    """

    course_id = None

    def is_valid_course(self):

        if settings.LMS_COURSE_VALIDATION_BASE_URL:
            uri = '{0}/{1}/info'.format(settings.LMS_COURSE_VALIDATION_BASE_URL, self.course_id)

            try:
                response = requests.get(uri, timeout=5)
            except requests.exceptions.Timeout:
                logger.error('Course validation timed out: {}'.format(uri))
                # consider the course valid if the LMS times out
                return True

            # pylint: disable=no-member
            return response.status_code == requests.codes.ok
        else:
            # all courses valid if LMS url isn't specified
            return True

    def dispatch(self, request, *args, **kwargs):
        if self.is_valid_course():
            return super(CourseValidMixin, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class CoursePermissionMixin(object):
    course_id = None
    user = None

    def can_view(self):
        return permissions.user_can_view_course(self.user, self.course_id)

    def dispatch(self, request, *args, **kwargs):
        if settings.ENABLE_COURSE_PERMISSIONS and not self.can_view():
            raise PermissionDenied

        return super(CoursePermissionMixin, self).dispatch(request, *args, **kwargs)


class CourseNavBarMixin(object):
    """
    Mixin to add navbar items to context.

    This mixin is intended for course views that have a course_id property.
    """

    # Primary nav item that should be displayed as active. This value MUST be overwritten by the child class.
    active_primary_nav_item = None

    # Secondary nav item that should be displayed as active. This value is optional.
    active_secondary_nav_item = None

    # Tertiary nav item that should be displayed as active. This value is optional.
    active_tertiary_nav_item = None

    # Items that will populate the secondary nav list. This value is optional.
    secondary_nav_items = []

    # Items that will populate the tertiary nav list. This value is optional.
    tertiary_nav_items = []

    def get_primary_nav_items(self):
        """
        Return the primary nav items.
        """

        items = [
            {
                'name': 'enrollment',
                'label': _('Enrollment'),
                'view': 'courses:enrollment_activity',
                'icon': 'fa-child'
            },
            {
                'name': 'engagement',
                'label': _('Engagement'),
                'view': 'courses:engagement_content',
                'icon': 'fa-bar-chart',
            }
        ]

        # Remove disabled items
        items = filter(is_feature_enabled, items)

        # Clean each item
        map(self.clean_item, items)

        return items

    def _build_nav_items(self, nav_items, active_item):
        # Deep copy the list since it is a list of dictionaries
        items = copy.deepcopy(nav_items)

        # Process only the nav items that are enabled
        items = filter(is_feature_enabled, items)

        for item in items:
            item['active'] = active_item == item['name']
            self.clean_item(item)

        return items

    def get_secondary_nav_items(self):
        """
        Return the secondary nav items.
        """
        return self._build_nav_items(self.secondary_nav_items, self.active_secondary_nav_item)

    def get_tertiary_nav_items(self):
        """
        Return the tertiary nav items.
        """
        return self._build_nav_items(self.tertiary_nav_items, self.active_tertiary_nav_item)

    def clean_item(self, item):
        """
        Remove extraneous keys from item and set the href value.
        """
        # Prevent page reload if user clicks on the active navbar item, otherwise navigate to the new page.
        if item.get('active', False):
            href = '#'
        else:
            href = reverse(item['view'], kwargs={'course_id': self.course_id})

        item['href'] = href

        # Delete entries that are no longer needed
        item.pop('view', None)
        item.pop('switch', None)

    def get_context_data(self, **kwargs):
        context = super(CourseNavBarMixin, self).get_context_data(**kwargs)

        primary_nav_items = self.get_primary_nav_items()
        secondary_nav_items = self.get_secondary_nav_items()
        tertiary_nav_items = self.get_tertiary_nav_items()

        # Get the active primary item and remove it from the list
        primary_nav_item = [i for i in primary_nav_items if i['name'] == self.active_primary_nav_item][0]
        primary_nav_items.remove(primary_nav_item)

        context.update({
            'primary_nav_item': primary_nav_item,
            'primary_nav_items': primary_nav_items,
            'secondary_nav_items': secondary_nav_items,
            'tertiary_nav_items': tertiary_nav_items
        })

        return context


class CourseView(LoginRequiredMixin, CourseValidMixin, CoursePermissionMixin, TemplateView):
    """
    Base course view.

    Adds conveniences such as course_id attribute, and handles 404s when retrieving data from the API.
    """
    client = None
    course = None
    course_id = None
    course_key = None
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.course_id = request.course_id
        self.course_key = request.course_key

        # some views will catch the NotFoundError to set data to a state that
        # the template can rendering a loading error message for the section
        try:
            return super(CourseView, self).dispatch(request, *args, **kwargs)
        except NotFoundError:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(CourseView, self).get_context_data(**kwargs)
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN, timeout=5)
        self.course = self.client.courses(self.course_id)
        return context


class CourseTemplateView(ContextSensitiveHelpMixin, CourseContextMixin, CourseView):
    update_message = None

    @property
    def help_token(self):
        # Rather than duplicate the definition, simply return the page name.
        return self.page_name

    def get_last_updated_message(self, last_updated):
        if last_updated:
            return self.update_message % self.format_last_updated_date_and_time(last_updated)
        else:
            return None

    @staticmethod
    def format_last_updated_date_and_time(d):
        return {'update_date': dateformat.format(d, settings.DATE_FORMAT), 'update_time': dateformat.format(d, 'g:i A')}


class CourseTemplateWithNavView(CourseNavBarMixin, CourseTemplateView):
    pass


class EnrollmentTemplateView(CourseTemplateWithNavView):
    """
    Base view for course enrollment pages.
    """
    secondary_nav_items = [
        {'name': 'activity', 'label': _('Activity'), 'view': 'courses:enrollment_activity'},
        {'name': 'demographics', 'label': _('Demographics'), 'view': 'courses:enrollment_demographics_age'},
        {'name': 'geography', 'label': _('Geography'), 'view': 'courses:enrollment_geography'},
    ]
    active_primary_nav_item = 'enrollment'


class EnrollmentDemographicsTemplateView(EnrollmentTemplateView):
    """
    Base view for course enrollment demographics pages.
    """
    active_secondary_nav_item = 'demographics'
    tertiary_nav_items = [
        {'name': 'age', 'label': _('Age'), 'view': 'courses:enrollment_demographics_age'},
        {'name': 'education', 'label': _('Education'), 'view': 'courses:enrollment_demographics_education'},
        {'name': 'gender', 'label': _('Gender'), 'view': 'courses:enrollment_demographics_gender'}
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


class EngagementTemplateView(CourseTemplateWithNavView):
    """
    Base view for course engagement pages.
    """
    secondary_nav_items = [
        # Translators: Content as in course content (e.g. things, not the feeling)
        {'name': 'content', 'label': _('Content'), 'view': 'courses:engagement_content'},
    ]
    active_primary_nav_item = 'engagement'


class CSVResponseMixin(object):
    csv_filename_suffix = None

    # pylint: disable=unused-argument
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(self.get_data(), content_type='text/csv', **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self._get_filename())
        return response

    def get_data(self):
        raise NotImplementedError

    def _get_filename(self):
        course_key = self.course_key
        course_id = '-'.join([course_key.org, course_key.course, course_key.run])
        filename = '{0}--{1}.csv'.format(course_id, self.csv_filename_suffix)
        return urllib.quote(filename)


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


class EngagementContentView(EngagementTemplateView):
    template_name = 'courses/engagement_content.html'
    page_title = _('Engagement Content')
    page_name = 'engagement_content'
    active_secondary_nav_item = 'content'

    # Translators: Do not translate UTC.
    update_message = _('Course engagement data was last updated %(update_date)s at %(update_time)s UTC.')

    def get_context_data(self, **kwargs):
        context = super(EngagementContentView, self).get_context_data(**kwargs)

        presenter = CourseEngagementPresenter(self.course_id)

        summary = None
        trends = None
        last_updated = None
        try:
            summary, trends = presenter.get_summary_and_trend_data()
            last_updated = summary['last_updated']
        except NotFoundError:
            logger.error("Failed to retrieve engagement content data for %s.", self.course_id)

        context['js_data']['course']['engagementTrends'] = trends
        context.update({
            'summary': summary,
            'update_message': self.get_last_updated_message(last_updated)
        })
        context['page_data'] = self.get_page_data(context)

        return context


class CourseEnrollmentDemographicsAgeCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-by-birth-year'

    def get_data(self):
        return self.course.enrollment(demographic.BIRTH_YEAR, data_format=data_format.CSV),


class CourseEnrollmentDemographicsEducationCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-by-education'

    def get_data(self):
        return self.course.enrollment(demographic.EDUCATION, data_format=data_format.CSV),


class CourseEnrollmentDemographicsGenderCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-by-gender'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.enrollment(demographic.GENDER, end_date=end_date, data_format=data_format.CSV),


class CourseEnrollmentByCountryCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-location'

    def get_data(self):
        return self.course.enrollment(demographic.LOCATION, data_format=data_format.CSV)


class CourseEnrollmentCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment'

    def get_data(self):
        _demographic = 'mode' if switch_is_active('display_verified_enrollment') else None
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.enrollment(_demographic, data_format=data_format.CSV, end_date=end_date)


class CourseEngagementActivityTrendCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'engagement-activity'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.activity(data_format=data_format.CSV, end_date=end_date)


class CourseHome(CourseTemplateView):
    template_name = 'courses/home.html'
    page_name = 'course_home'
    page_title = _('Course Home')

    def get_navbar_items(self):
        return [
            {
                'name': 'enrollment',
                'label': _('Enrollment'),
                'view': 'courses:enrollment_activity',
                'icon': 'fa-child'
            },
            {
                'name': 'engagement',
                'label': _('Engagement'),
                'view': 'courses:engagement_content',
                'icon': 'fa-bar-chart',
            }
        ]

    def get_table_items(self):
        table_items = [
            {
                'name': _('Enrollment'),
                'icon': 'fa-child',
                'heading': _('Who are my students?'),
                'items': [
                    {
                        'title': _('How many students are in my course?'),
                        'view': 'courses:enrollment_activity',
                        'breadcrumbs': [_('Activity')]
                    },
                    {
                        'title': _('What age are my students?'),
                        'view': 'courses:enrollment_demographics_age',
                        'breadcrumbs': [_('Demographics'), _('Age')]
                    },
                    {
                        'title': _('What is the educational background of my students?'),
                        'view': 'courses:enrollment_demographics_education',
                        'breadcrumbs': [_('Demographics'), _('Education')]
                    },
                    {
                        'title': _('What is the gender breakdown of my students?'),
                        'view': 'courses:enrollment_demographics_gender',
                        'breadcrumbs': [_('Demographics'), _('Gender')]
                    },
                    {
                        'title': _('Where are my students from?'),
                        'view': 'courses:enrollment_geography',
                        'breadcrumbs': [_('Geography')]
                    },
                ],
            },
            {
                'name': _('Engagement'),
                'icon': 'fa-bar-chart',
                'heading': _('What are my students engaging with in my course?'),
                'items': [
                    {
                        'title': _('How many students are engaged in my course?'),
                        'view': 'courses:engagement_content',
                        'breadcrumbs': [_('Content')]
                    }
                ]
            }
        ]
        return table_items

    def get_context_data(self, **kwargs):
        context = super(CourseHome, self).get_context_data(**kwargs)
        context.update({
            'navbar_items': self.get_navbar_items(),
            'table_items': self.get_table_items()
        })

        context['page_data'] = self.get_page_data(context)
        return context


class CourseIndex(LoginRequiredMixin, TrackedViewMixin, LazyEncoderMixin, TemplateView):
    template_name = 'courses/index.html'
    page_name = 'course_index'

    def get_context_data(self, **kwargs):
        context = super(CourseIndex, self).get_context_data(**kwargs)

        courses = permissions.get_user_course_permissions(self.request.user)

        if not courses:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        context['courses'] = sorted(courses)
        context['page_data'] = self.get_page_data(context)

        return context
