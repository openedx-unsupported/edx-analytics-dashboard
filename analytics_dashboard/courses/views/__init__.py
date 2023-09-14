import copy
import json
import logging
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from analyticsclient.client import Client
from analyticsclient.exceptions import ClientError, NotFoundError
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils import dateformat
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from django.views import View
from django.views.generic import TemplateView
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from opaque_keys.edx.keys import CourseKey
from waffle import switch_is_active

from analytics_dashboard.core.exceptions import ServiceUnavailableError
from analytics_dashboard.core.utils import (
    CourseStructureApiClient,
    sanitize_cache_key,
    translate_dict_values,
)
from analytics_dashboard.courses import permissions
from analytics_dashboard.courses.presenters.performance import CourseReportDownloadPresenter
from analytics_dashboard.courses.serializers import LazyEncoder
from analytics_dashboard.courses.utils import get_page_name, is_feature_enabled
from analytics_dashboard.courses.waffle import age_available
from analytics_dashboard.help.views import ContextSensitiveHelpMixin

logger = logging.getLogger(__name__)


class CourseAPIMixin:
    access_token = None
    course_api_enabled = False
    course_api = None
    course_id = None

    @cached_property
    def course_info(self):
        """
        Returns course info.

        All requests for course info should be made against this property to take advantage of caching.
        """
        return self.get_course_info(self.course_id)

    def dispatch(self, request, *args, **kwargs):
        self.course_api_enabled = switch_is_active('enable_course_api')

        if self.course_api_enabled and request.user.is_authenticated:
            self.course_api = CourseStructureApiClient(
                settings.BACKEND_SERVICE_EDX_OAUTH2_PROVIDER_URL,
                settings.BACKEND_SERVICE_EDX_OAUTH2_KEY,
                settings.BACKEND_SERVICE_EDX_OAUTH2_SECRET,
            )

        return super().dispatch(request, *args, **kwargs)

    def _course_detail_cache_key(self, course_id):
        return sanitize_cache_key(f'course_{course_id}_details')

    def get_course_info(self, course_id):
        """
        Retrieve course info from the Course API.

        Retrieved data is cached.

        Arguments
            course_id       -- ID of the course for which data should be retrieved
        """
        key = self._course_detail_cache_key(course_id)
        info = cache.get(key)

        if not info:
            try:
                logger.debug("Retrieving detail for course: %s", course_id)
                info = self.course_api.get(
                    urljoin(settings.COURSE_API_URL + '/', f'courses/{course_id}')
                ).json()
                cache.set(key, info)
            except HTTPError as e:
                logger.error("Unable to retrieve course info for %s: %s", course_id, e)
                info = {}

        return info

    def get_courses(self):
        # Check the cache for the user's courses
        key = sanitize_cache_key(f'user_{self.request.user.pk}_courses')
        courses = cache.get(key)

        # If no cached courses, iterate over the data from the course API.
        if not courses:
            courses = []
            page = 1

            while page:
                try:
                    logger.debug('Retrieving page %d of course info...', page)
                    response = self.course_api.get(
                        urljoin(settings.COURSE_API_URL + '/', 'courses/'),
                        params={
                            'page': page,
                            'page_size': 100,
                        }
                    ).json()
                    course_details = response['results']

                    # Cache the information so that it doesn't need to be retrieved later.
                    for course in course_details:
                        course_id = course['id']
                        _key = self._course_detail_cache_key(course_id)
                        cache.set(_key, course)

                    courses += course_details

                    if response['pagination']['next']:
                        page += 1
                    else:
                        page = None
                        logger.debug('Completed retrieval of course info. Retrieved info for %d courses.', len(courses))
                except HTTPError as e:
                    logger.error("Unable to retrieve course data: %s", e)
                    page = None
                    break

        cache.set(key, courses)
        return courses


class TrackedViewMixin:
    """
    Adds tracking variables to the context passed to Javascript.
    """

    # Page name used for usage tracking/analytics
    page_name = {
        'scope': '',
        'lens': '',
        'report': '',
        'depth': '',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.page_name['name'] = get_page_name(self.page_name)
        context['js_data'] = context.get('js_data', {})
        context['js_data'].update({
            'tracking': {
                'segmentApplicationId': settings.SEGMENT_IO_KEY,  # None will translate to 'null'
                'page': self.page_name
            }
        })
        return context


class LazyEncoderMixin:
    def get_page_data(self, context):
        """ Returns JSON serialized data with lazy translations converted. """
        if 'js_data' in context:
            return json.dumps(context['js_data'], cls=LazyEncoder)
        return None


class CourseContextMixin(CourseAPIMixin, TrackedViewMixin, LazyEncoderMixin):
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
        context = super().get_context_data(**kwargs)
        context.update(self.get_default_data())

        user = self.request.user
        context['js_data'] = context.get('js_data', {})
        context['js_data'].update({
            'course': {
                'courseId': self.course_id,
                'org': CourseKey.from_string(self.course_id).org
            },
            'user': {
                'username': user.get_username(),
                'userTrackingID': permissions.get_user_tracking_id(self.request.user),
                'name': user.get_full_name(),
                'email': user.email,
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
            'page_subtitle': self.page_subtitle,
        }

        if self.course_api_enabled and switch_is_active('display_course_name_in_nav'):
            context['course_name'] = self.course_info.get('name')

        return context


class CourseValidMixin:
    """
    Mixin that checks the validity of a course ID against the LMS.
    """

    course_id = None

    def is_valid_course(self):

        if settings.LMS_COURSE_VALIDATION_BASE_URL:
            uri = f'{settings.LMS_COURSE_VALIDATION_BASE_URL}/{self.course_id}/info'

            try:
                response = requests.get(uri, timeout=settings.LMS_DEFAULT_TIMEOUT)
            except requests.exceptions.Timeout:
                logger.error('Course validation timed out: %s', uri)
                # consider the course valid if the LMS times out
                return True

            # pylint: disable=no-member
            return response.status_code == requests.codes.ok
        # all courses valid if LMS url isn't specified
        return True

    def dispatch(self, request, *args, **kwargs):
        if self.is_valid_course():
            return super().dispatch(request, *args, **kwargs)

        raise Http404


class CoursePermissionMixin:
    course_id = None
    user = None

    def can_view(self):
        return permissions.user_can_view_course(self.user, self.course_id)

    def dispatch(self, request, *args, **kwargs):
        if settings.ENABLE_COURSE_PERMISSIONS and not self.can_view():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class CourseNavBarMixin:
    """
    Mixin to add navbar items to context.

    This mixin is intended for course views that have a course_id property.
    """

    # Primary nav item that should be displayed as active. This value should be overwritten by the child class.
    active_primary_nav_item = None

    # Secondary nav item that should be displayed as active. This value is optional.
    active_secondary_nav_item = None

    # Tertiary nav item that should be displayed as active. This value is optional.
    active_tertiary_nav_item = None

    # Items that will populate the secondary nav list. This value is optional.
    secondary_nav_items = []

    # Items that will populate the tertiary nav list. This value is optional.
    tertiary_nav_items = []

    def get_primary_nav_items(self, request):
        """
        Return the primary nav items.
        """

        items = [
            {
                'name': 'enrollment',
                'text': gettext_noop('Enrollment'),
                'view': 'courses:enrollment:activity',
                'icon': 'fa-child',
                'fragment': '',
                'scope': 'course',
                'lens': 'enrollment',
                'report': 'activity',
                'depth': ''
            },
            {
                'name': 'engagement',
                'text': gettext_noop('Engagement'),
                'view': 'courses:engagement:content',
                'icon': 'fa-bar-chart',
                'fragment': '',
                'scope': 'course',
                'lens': 'engagement',
                'report': 'content',
                'depth': ''
            },
            {
                'name': 'performance',
                'text': gettext_noop('Performance'),
                'view': 'courses:performance:graded_content',
                'icon': 'fa-check-square-o',
                'switch': 'enable_course_api',
                'fragment': '',
                'scope': 'course',
                'lens': 'performance',
                'report': 'graded',
                'depth': ''
            }

        ]

        translate_dict_values(items, ('text',))

        # Remove disabled items
        items = [item for item in items if is_feature_enabled(item, request)]

        # Clean each item
        list(map(self.clean_item, items))

        return items

    def _build_nav_items(self, nav_items, active_item, request):
        # Deep copy the list since it is a list of dictionaries
        items = copy.deepcopy(nav_items)

        # Process only the nav items that are enabled
        items = [item for item in items if is_feature_enabled(item, request)]

        for item in items:
            item['active'] = active_item == item['name']
            self.clean_item(item)

        return items

    def get_secondary_nav_items(self, request):
        """
        Return the secondary nav items.
        """
        return self._build_nav_items(self.secondary_nav_items, self.active_secondary_nav_item, request)

    def get_tertiary_nav_items(self, request):
        """
        Return the tertiary nav items.
        """
        return self._build_nav_items(self.tertiary_nav_items, self.active_tertiary_nav_item, request)

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
        context = super().get_context_data(**kwargs)

        primary_nav_items = self.get_primary_nav_items(self.request)
        secondary_nav_items = self.get_secondary_nav_items(self.request)
        tertiary_nav_items = self.get_tertiary_nav_items(self.request)

        # Get the active primary item and remove it from the list
        primary_nav_item = None
        if self.active_primary_nav_item:
            navs = [i for i in primary_nav_items if i['name'] == self.active_primary_nav_item]
            if navs:
                primary_nav_item = navs[0]
                primary_nav_items.remove(primary_nav_item)

        context.update({
            'primary_nav_item': primary_nav_item,
            'primary_nav_items': primary_nav_items,
            'secondary_nav_items': secondary_nav_items,
            'tertiary_nav_items': tertiary_nav_items
        })

        return context


class AnalyticsV0Mixin(View):
    """
    put views on analytics v0 unless v1 is requested
    this mixin will be removed when transition is complete
    """
    analytics_client = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        api_version = request.GET.get('v', '0')
        analytics_base_url = settings.DATA_API_URL_V1 if api_version == '1' else settings.DATA_API_URL
        self.analytics_client = Client(base_url=analytics_base_url,
                                       auth_token=settings.DATA_API_AUTH_TOKEN,
                                       timeout=settings.ANALYTICS_API_DEFAULT_TIMEOUT)


class AnalyticsV1Mixin(View):
    """
    put views on analytics v1 if it is available, otherwise v0
    still preserves a v0 escape valve during transition
    but that will be removed from this class when we're done
    """
    analytics_client = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        v_default = '0'
        if settings.DATA_API_V1_ENABLED:
            v_default = '1'

        api_version = request.GET.get('v', v_default)
        analytics_base_url = settings.DATA_API_URL_V1 if api_version == '1' else settings.DATA_API_URL
        self.analytics_client = Client(base_url=analytics_base_url,
                                       auth_token=settings.DATA_API_AUTH_TOKEN,
                                       timeout=settings.ANALYTICS_API_DEFAULT_TIMEOUT)


class CourseView(LoginRequiredMixin, CourseValidMixin, CoursePermissionMixin, TemplateView):
    """
    Base course view.

    Adds conveniences such as course_id attribute, and handles 404s when retrieving data from the API.
    """
    course = None
    course_id = None
    course_key = None
    user = None
    api_version = None

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.course_id = request.course_id
        self.course_key = request.course_key

        # some views will catch the NotFoundError to set data to a state that
        # the template can rendering a loading error message for the section
        try:
            return super().dispatch(request, *args, **kwargs)
        except NotFoundError as e:
            logger.error('The requested data from the Analytics Data API was not found: %s', e)
            raise Http404 from e
        except ClientError as e:
            logger.error('An error occurred while retrieving data from the Analytics Data API: %s', e)
            raise

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.course = self.analytics_client.courses(self.course_id)
        return context


class LastUpdatedView:
    def get_last_updated_message(self, last_updated):
        if last_updated:
            return self.update_message % self.format_last_updated_date_and_time(last_updated)
        return None

    @staticmethod
    def format_last_updated_date_and_time(d):
        return {'update_date': dateformat.format(d, settings.DATE_FORMAT),
                'update_time': dateformat.format(d, settings.TIME_FORMAT)}


class CourseTemplateView(LastUpdatedView, ContextSensitiveHelpMixin, CourseContextMixin, CourseView):
    update_message = None

    @property
    def help_token(self):
        # Rather than duplicate the definition, simply return the page name.
        page_name = get_page_name(self.page_name)
        if not page_name:
            page_name = 'default'
        return page_name


class CourseTemplateWithNavView(CourseNavBarMixin, CourseTemplateView):
    pass


class CourseHome(AnalyticsV0Mixin, CourseTemplateWithNavView):
    template_name = 'courses/home.html'
    page_name = {
        'scope': 'course',
        'lens': 'home',
        'report': '',
        'depth': ''
    }
    page_title = _('Course Home')

    def get_table_items(self):
        items = []

        enrollment_subitems = [
            {
                'title': gettext_noop('How many learners are in my course?'),
                'view': 'courses:enrollment:activity',
                'breadcrumbs': [_('Activity')],
                'fragment': '',
                'scope': 'course',
                'lens': 'enrollment',
                'report': 'activity',
                'depth': ''
            }]
        if age_available():
            enrollment_subitems = enrollment_subitems + [
                {
                    'title': gettext_noop('How old are my learners?'),
                    'view': 'courses:enrollment:demographics_age',
                    'breadcrumbs': [_('Demographics'), _('Age')],
                    'fragment': '',
                    'scope': 'course',
                    'lens': 'enrollment',
                    'report': 'demographics',
                    'depth': 'age'
                }]
        enrollment_subitems = enrollment_subitems + [
            {
                'title': gettext_noop('What level of education do my learners have?'),
                'view': 'courses:enrollment:demographics_education',
                'breadcrumbs': [_('Demographics'), _('Education')],
                'fragment': '',
                'scope': 'course',
                'lens': 'enrollment',
                'report': 'demographics',
                'depth': 'education'
            },
            {
                'title': gettext_noop('What is the learner gender breakdown?'),
                'view': 'courses:enrollment:demographics_gender',
                'breadcrumbs': [_('Demographics'), _('Gender')],
                'fragment': '',
                'scope': 'course',
                'lens': 'enrollment',
                'report': 'demographics',
                'depth': 'gender'
            },
            {
                'title': gettext_noop('Where are my learners?'),
                'view': 'courses:enrollment:geography',
                'breadcrumbs': [_('Geography')],
                'fragment': '',
                'scope': 'course',
                'lens': 'enrollment',
                'report': 'geography',
                'depth': ''
            },
        ]

        enrollment_items = {
            'name': _('Enrollment'),
            'icon': 'fa-child',
            'heading': _('Who are my learners?'),
            'items': enrollment_subitems,
        }
        items.append(enrollment_items)

        engagement_items = {
            'name': _('Engagement'),
            'icon': 'fa-bar-chart',
            'heading': _('What are learners doing in my course?'),
            'items': [
                {
                    'title': gettext_noop('How many learners are interacting with my course?'),
                    'view': 'courses:engagement:content',
                    'breadcrumbs': [_('Content')],
                    'fragment': '',
                    'scope': 'course',
                    'lens': 'engagement',
                    'report': 'content',
                    'depth': ''
                }
            ]
        }
        if switch_is_active('enable_engagement_videos_pages'):
            engagement_items['items'].append({
                'title': gettext_noop('How did learners interact with course videos?'),
                'view': 'courses:engagement:videos',
                'breadcrumbs': [_('Videos')],
                'fragment': '',
                'scope': 'course',
                'lens': 'engagement',
                'report': 'videos',
                'depth': ''
            })

        items.append(engagement_items)

        if self.course_api_enabled:
            subitems = [{
                'title': gettext_noop('How are learners doing on graded course assignments?'),
                'view': 'courses:performance:graded_content',
                'breadcrumbs': [_('Graded Content')],
                'fragment': '',
                'scope': 'course',
                'lens': 'performance',
                'report': 'graded',
                'depth': ''
            }, {
                'title': gettext_noop('How are learners doing on ungraded exercises?'),
                'view': 'courses:performance:ungraded_content',
                'breadcrumbs': [_('Ungraded Problems')],
                'fragment': '',
                'scope': 'course',
                'lens': 'performance',
                'report': 'ungraded',
                'depth': ''
            }]

            if switch_is_active('enable_performance_learning_outcome'):
                subitems.append({
                    'title': gettext_noop('What is the breakdown for course learning outcomes?'),
                    'view': 'courses:performance:learning_outcomes',
                    'breadcrumbs': [_('Learning Outcomes')],
                    'fragment': '',
                    'scope': 'course',
                    'lens': 'performance',
                    'report': 'outcomes',
                    'depth': ''
                })

            if switch_is_active('enable_problem_response_download'):
                try:
                    info = CourseReportDownloadPresenter(self.course_id, self.analytics_client).get_report_info(
                        report_name=CourseReportDownloadPresenter.PROBLEM_RESPONSES
                    )
                except NotFoundError:
                    info = {}
                if 'download_url' in info:
                    # A problem response report CSV is available:
                    subitems.append({
                        'title': gettext_noop('How are learners responding to questions?'),
                        'view': 'courses:csv:performance_problem_responses',
                        'breadcrumbs': [_('Problem Response Report')],
                        'format': 'csv',
                    })

            items.append({
                'name': _('Performance'),
                'icon': 'fa-check-square-o',
                'heading': _('How are learners doing on course assignments?'),
                'items': subitems
            })

        translate_dict_values(items, ('name',))
        for item in items:
            translate_dict_values(item['items'], ('title',))

        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'table_items': self.get_table_items()
        })

        context['page_data'] = self.get_page_data(context)

        overview_data = []
        if self.course_api_enabled:
            if switch_is_active('display_course_name_in_nav'):
                # Translators: 'Course ID' is 'Course Identifier', the unique code that identifies the course
                overview_data.append((_('Course ID'), self.course_id))
            else:
                overview_data.append((_('Course Name'), self.course_info.get('name')))

            def parse_course_date(date_str):
                return datetime.strptime(date_str, CourseStructureApiClient.DATETIME_FORMAT) if date_str else None

            def format_date(date):
                return dateformat.format(date, settings.DATE_FORMAT) if date else "--"

            start_date = parse_course_date(self.course_info.get('start'))
            end_date = parse_course_date(self.course_info.get('end'))
            todays_date = datetime.now()
            status_str = '--'
            if start_date:
                if todays_date >= start_date:
                    in_progress = (end_date is None or end_date > todays_date)
                    # Translators: 'In Progress' and 'Ended' refer to whether learners are
                    # actively using the course or it is over.
                    status_str = _('In Progress') if in_progress else _('Ended')
                else:
                    # Translators: This refers to a course that has not yet begun.
                    status_str = _('Not Started Yet')
            overview_data += [
                (_('Start Date'), format_date(start_date)),
                (_('End Date'), format_date(end_date)),
                (_('Status'), status_str),
            ]

        context['course_overview'] = overview_data

        external_tools = []

        if settings.LMS_COURSE_SHORTCUT_BASE_URL:
            external_tools.append({
                'title': gettext_noop('Instructor Dashboard'),
                'url': f"{settings.LMS_COURSE_SHORTCUT_BASE_URL}/{self.course_id}/instructor",
                'icon': 'fa-dashboard',
            })
            external_tools.append({
                'title': gettext_noop('Courseware'),
                'url': f"{settings.LMS_COURSE_SHORTCUT_BASE_URL}/{self.course_id}/courseware",
                'icon': 'fa-pencil-square-o',
            })
        if settings.CMS_COURSE_SHORTCUT_BASE_URL:
            external_tools.append({
                'title': 'Studio',
                'translated_title': 'Studio',  # As a brand name, "Studio" is not translated.
                'url': f"{settings.CMS_COURSE_SHORTCUT_BASE_URL}/{self.course_id}",
                'icon': 'fa-sliders',
            })

        translate_dict_values(external_tools, ('title',))
        context['external_course_tools'] = external_tools

        return context


class CourseStructureExceptionMixin:
    """
    Catches exceptions from the course structure API.  This mixin should be included before
    CourseAPIMixin.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except RequestException as e:
            # Return the appropriate response if a 404 occurred.
            response = getattr(e, 'response')
            if response is not None:
                if response.status_code == 404:
                    logger.info('Course API data not found for %s: %s', self.course_id, e)
                    raise Http404 from e
                if response.status_code == 503:
                    raise ServiceUnavailableError from e

            # Not a 404. Continue raising the error.
            logger.error('An error occurred while using Slumber to communicate with an API: %s', e)
            raise


class CourseStructureMixin:
    """
    Retrieves and sets section and subsection IDs and added the sections, subsections,
    and subsection children (e.g. videos, problems) to the context.

    The presenter is expected to be derived from CourseAPIPresenterMixin.
    """

    section_id = None
    subsection_id = None
    presenter = None  # course structure presenter

    def dispatch(self, request, *args, **kwargs):
        self.section_id = kwargs.get('section_id', None)
        self.subsection_id = kwargs.get('subsection_id', None)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sections': self.presenter.sections(),
        })

        if self.section_id:
            section = self.presenter.section(self.section_id)
            if section:
                context.update({
                    'section': section,
                    'subsections': self.presenter.subsections(self.section_id)
                })
            else:
                raise Http404

            if self.subsection_id:
                subsection = self.presenter.subsection(self.section_id, self.subsection_id)
                if subsection:
                    context.update({
                        'subsection': subsection,
                        'subsection_children': self.presenter.subsection_children(self.section_id, self.subsection_id)
                    })
                else:
                    raise Http404

        return context

    def set_primary_content(self, context, primary_data):
        context['js_data']['course'].update({
            'primaryContent': primary_data,
            'hasData': self.presenter.blocks_have_data(primary_data)
        })
