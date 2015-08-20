import copy
import json
import logging
import re

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import dateformat
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
import requests
from slumber.exceptions import (HttpClientError, SlumberBaseException)
from waffle import switch_is_active

from analyticsclient.client import Client
from analyticsclient.exceptions import (ClientError, NotFoundError)


from common.clients import CourseStructureApiClient

from core.exceptions import ServiceUnavailableError
from core.utils import sanitize_cache_key

from courses import permissions
from courses.serializers import LazyEncoder
from courses.utils import is_feature_enabled

from help.views import ContextSensitiveHelpMixin


logger = logging.getLogger(__name__)


class CourseAPIMixin(object):
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

        if self.course_api_enabled and request.user.is_authenticated():
            self.access_token = settings.COURSE_API_KEY or request.user.access_token
            self.course_api = CourseStructureApiClient(settings.COURSE_API_URL, self.access_token).courses

        return super(CourseAPIMixin, self).dispatch(request, *args, **kwargs)

    def _course_detail_cache_key(self, course_id):
        return sanitize_cache_key(u'course_{}_details'.format(course_id))

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
                info = self.course_api(course_id).get()
                cache.set(key, info)
            except HttpClientError as e:
                logger.error("Unable to retrieve course info for %s: %s", course_id, e)
                info = {}

        return info

    def get_courses(self):
        # Check the cache for the user's courses
        key = sanitize_cache_key(u'user_{}_courses'.format(self.request.user.pk))
        courses = cache.get(key)

        # If no cached courses, iterate over the data from the course API.
        if not courses:
            courses = []
            page = 1

            while page:
                try:
                    logger.debug('Retrieving page %d of course info...', page)
                    response = self.course_api.get(page=page, page_size=100)
                    course_details = response['results']

                    # Cache the information so that it doesn't need to be retrieved later.
                    for course in course_details:
                        course_id = course['id']
                        _key = self._course_detail_cache_key(course_id)
                        cache.set(_key, course)

                    courses += course_details

                    if response['next']:
                        page += 1
                    else:
                        page = None
                        logger.debug('Completed retrieval of course info. Retrieved info for %d courses.', len(courses))
                except HttpClientError as e:
                    logger.error("Unable to retrieve course data: %s", e)
                    page = None
                    break

        cache.set(key, courses)
        return courses


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
        context = super(CourseContextMixin, self).get_context_data(**kwargs)
        context.update(self.get_default_data())

        user = self.request.user
        context['js_data'] = context.get('js_data', {})
        context['js_data'].update({
            'course': {
                'courseId': self.course_id
            },
            'user': {
                'username': user.get_username(),
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
                logger.error('Course validation timed out: %s', uri)
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

    def get_primary_nav_items(self):
        """
        Return the primary nav items.
        """

        items = [
            {
                'name': 'enrollment',
                'label': _('Enrollment'),
                'view': 'courses:enrollment:activity',
                'icon': 'fa-child'
            },
            {
                'name': 'engagement',
                'label': _('Engagement'),
                'view': 'courses:engagement:content',
                'icon': 'fa-bar-chart',
            },
            {
                'name': 'performance',
                'label': _('Performance'),
                'view': 'courses:performance:graded_content',
                'icon': 'fa-check-square-o',
                'switch': 'enable_course_api',
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
        primary_nav_item = None
        if self.active_primary_nav_item:
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
        except NotFoundError as e:
            logger.error('The requested data from the Analytics Data API was not found: %s', e)
            raise Http404
        except ClientError as e:
            logger.error('An error occurred while retrieving data from the Analytics Data API: %s', e)
            raise

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


class CourseHome(CourseTemplateWithNavView):
    template_name = 'courses/home.html'
    page_name = 'course_home'
    page_title = _('Course Home')

    def get_table_items(self):
        items = []

        enrollment_items = {
            'name': _('Enrollment'),
            'icon': 'fa-child',
            'heading': _('Who are my students?'),
            'items': [
                {
                    'title': _('How many students are in my course?'),
                    'view': 'courses:enrollment:activity',
                    'breadcrumbs': [_('Activity')]
                },
                {
                    'title': _('How old are my students?'),
                    'view': 'courses:enrollment:demographics_age',
                    'breadcrumbs': [_('Demographics'), _('Age')]
                },
                {
                    'title': _('What level of education do my students have?'),
                    'view': 'courses:enrollment:demographics_education',
                    'breadcrumbs': [_('Demographics'), _('Education')]
                },
                {
                    'title': _('What is the student gender breakdown?'),
                    'view': 'courses:enrollment:demographics_gender',
                    'breadcrumbs': [_('Demographics'), _('Gender')]
                },
                {
                    'title': _('Where are my students?'),
                    'view': 'courses:enrollment:geography',
                    'breadcrumbs': [_('Geography')]
                },
            ],
        }
        items.append(enrollment_items)

        engagement_items = {
            'name': _('Engagement'),
            'icon': 'fa-bar-chart',
            'heading': _('What are students doing in my course?'),
            'items': [
                {
                    'title': _('How many students are interacting with my course?'),
                    'view': 'courses:engagement:content',
                    'breadcrumbs': [_('Content')]
                }
            ]
        }
        if switch_is_active('enable_engagement_videos_pages'):
            engagement_items['items'].append({
                'title': _('How did students interact with course videos?'),
                'view': 'courses:engagement:videos',
                'breadcrumbs': [_('Videos')]
            })

        items.append(engagement_items)

        if self.course_api_enabled:
            items.append({
                'name': _('Performance'),
                'icon': 'fa-check-square-o',
                'heading': _('How are students doing on course assignments?'),
                'items': [
                    {
                        'title': _('How are students doing on graded course assignments?'),
                        'view': 'courses:performance:graded_content',
                        'breadcrumbs': [_('Graded Content')]
                    },
                    {
                        'title': _('How are students doing on ungraded exercises?'),
                        'view': 'courses:performance:ungraded_content',
                        'breadcrumbs': [_('Ungraded Problems')]
                    }
                ]
            })

        return items

    def get_context_data(self, **kwargs):
        context = super(CourseHome, self).get_context_data(**kwargs)
        context.update({
            'table_items': self.get_table_items()
        })

        context['page_data'] = self.get_page_data(context)
        return context


class CourseIndex(CourseAPIMixin, LoginRequiredMixin, TrackedViewMixin, LazyEncoderMixin, TemplateView):
    template_name = 'courses/index.html'
    page_name = 'course_index'

    def get_context_data(self, **kwargs):
        context = super(CourseIndex, self).get_context_data(**kwargs)

        courses = permissions.get_user_course_permissions(self.request.user)

        if not courses:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        courses = self._create_course_list(courses)
        context['courses'] = courses
        context['page_data'] = self.get_page_data(context)

        return context

    def _create_course_list(self, course_ids):
        info = []
        course_data = {}

        if self.course_api_enabled and switch_is_active('display_names_for_course_index'):

            # Get data for all courses in a single API call.
            _api_courses = self.get_courses()

            # Create a lookup table from the data.
            for course in _api_courses:
                course_data[course['id']] = course['name']

        for course_id in course_ids:
            info.append({'key': course_id, 'name': course_data.get(course_id)})

        info.sort(key=lambda course: (course.get('name', '') or course.get('key', '') or '').lower())

        return info


class CourseStructureExceptionMixin(object):
    """
    Catches exceptions from the course structure API.  This mixin should be included before
    CourseAPIMixin.
    """

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(CourseStructureExceptionMixin, self).dispatch(request, *args, **kwargs)
        except SlumberBaseException as e:
            # Return the appropriate response if a 404 occurred.
            response = getattr(e, 'response')
            if response is not None:
                if response.status_code == 404:
                    logger.info('Course API data not found for %s: %s', self.course_id, e)
                    raise Http404
                elif response.status_code == 503:
                    raise ServiceUnavailableError

            # Not a 404. Continue raising the error.
            logger.error('An error occurred while using Slumber to communicate with an API: %s', e)
            raise


class CourseStructureMixin(object):
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
        return super(CourseStructureMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseStructureMixin, self).get_context_data(**kwargs)
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
