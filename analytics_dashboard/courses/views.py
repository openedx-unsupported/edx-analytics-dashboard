import copy
import datetime
import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from braces.views import LoginRequiredMixin
from analyticsclient import data_format, demographic
from analyticsclient.client import Client
from analyticsclient.exceptions import NotFoundError

from courses import permissions
from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter
from courses.utils import get_formatted_date, get_formatted_date_time, is_feature_enabled


class CourseContextMixin(object):
    """
    Adds default course context data.

    Use primarily with templated views where data needs to be passed to Javascript.
    """
    # Title displayed on the page
    page_title = None

    # Page name used for usage tracking/analytics
    page_name = None

    def get_context_data(self, **kwargs):
        context = super(CourseContextMixin, self).get_context_data(**kwargs)
        context.update(self.get_default_data())
        return context

    def get_default_data(self):
        """
        Returns default data for the pages (context and javascript data).
        """
        # TODO: Use real course data
        user = self.request.user
        context = {
            'user_name': user.get_full_name(),
            'user_id': user.get_username(),
            'user_email': user.email,
            'course_number': 'MITx 7.3423',
            'course_title': 'Introduction to Awesomeness',
            'course_id': self.course_id,
            'page_title': self.page_title,
            'js_data': {
                'course': {
                    'courseId': self.course_id
                },
                'tracking': {
                    'segmentApplicationId': settings.SEGMENT_IO_KEY,  # None will translate to 'null'
                    'page': self.page_name
                },
                'user': {
                    'userId': user.get_username(),
                    'userName': user.get_full_name(),
                    'userEmail': user.email,
                },
            }
        }

        return context


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

    # Items that will populate the secondary nav list. This value is optional.
    secondary_nav_items = []

    def get_primary_nav_items(self):
        """
        Return the primary nav items.
        """

        items = [
            {
                'label': 'Overview',
                'view': 'courses:overview',
                'icon': 'fa-tachometer',
                'switch': 'navbar_display_overview'
            },
            {
                'label': 'Enrollment',
                'view': 'courses:enrollment_activity',
                'icon': 'fa-child'
            },
            {
                'label': 'Engagement',
                'view': 'courses:engagement_content',
                'icon': 'fa-tasks',
                'switch': 'navbar_display_engagement'
            }
        ]

        # Remove disabled items
        items = filter(is_feature_enabled, items)

        # Clean each item
        map(self.clean_item, items)

        return items

    def get_secondary_nav_items(self):
        """
        Return the secondary nav items.
        """

        # Deep copy the list since it is a list of dictionaries
        items = copy.deepcopy(self.secondary_nav_items)

        # Process only the nav items that are enabled
        items = filter(is_feature_enabled, items)

        for item in items:
            item['active'] = self.active_secondary_nav_item == item['label']
            self.clean_item(item)

        return items

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

        # Get the active primary item and remove it from the list
        primary_nav_item = [i for i in primary_nav_items if i['label'] == self.active_primary_nav_item][0]
        primary_nav_items.remove(primary_nav_item)

        context.update({
            'primary_nav_item': primary_nav_item,
            'primary_nav_items': primary_nav_items,
            'secondary_nav_items': secondary_nav_items
        })

        return context


class CourseView(LoginRequiredMixin, CoursePermissionMixin, TemplateView):
    """
    Base course view.

    Adds conveniences such as course_id attribute, and handles 404s when retrieving data from the API.
    """
    client = None
    course = None
    course_id = None
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.course_id = kwargs['course_id']

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


class CourseTemplateView(CourseContextMixin, CourseNavBarMixin, CourseView):
    pass


class EnrollmentTemplateView(CourseTemplateView):
    """
    Base view for course enrollment pages.
    """
    secondary_nav_items = [
        {'label': 'Activity', 'view': 'courses:enrollment_activity'},
        {'label': 'Geography', 'view': 'courses:enrollment_geography'},
    ]
    active_primary_nav_item = 'Enrollment'


class EngagementTemplateView(CourseTemplateView):
    """
    Base view for course engagement pages.
    """
    secondary_nav_items = [
        {'label': 'Content', 'view': 'courses:engagement_content', 'switch': 'navbar_display_engagement_content'},
    ]
    active_primary_nav_item = 'Engagement'


class CSVResponseMixin(object):
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(context['data'], content_type='text/csv',
                                **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            context['filename'])
        return response


class JSONResponseMixin(object):
    def render_to_response(self, context, **response_kwargs):
        content = json.dumps(context['data'])
        return HttpResponse(content, content_type='application/json',
                            **response_kwargs)


class EnrollmentActivityView(EnrollmentTemplateView):
    template_name = 'courses/enrollment_activity.html'
    page_title = 'Enrollment Activity'
    page_name = 'enrollment_activity'
    active_secondary_nav_item = 'Activity'

    # pylint: disable=line-too-long
    def get_context_data(self, **kwargs):
        context = super(EnrollmentActivityView, self).get_context_data(**kwargs)

        tooltips = {
            'current_enrollment': 'Students enrolled in course.',
            'enrollment_change_last_1_days': 'Change in enrollment for the last full day (00:00-23:59 UTC).',
            'enrollment_change_last_7_days': 'Change in enrollment during the last 7 days (through 23:59 UTC).',
            'enrollment_change_last_30_days': 'Change in enrollment during the last 30 days (through 23:59 UTC).'
        }

        presenter = CourseEnrollmentPresenter(self.course_id)

        try:
            summary = presenter.get_summary()
            end_date = summary['date']
            start_date = end_date - datetime.timedelta(days=60)
            end_date = end_date + datetime.timedelta(days=1)
            data = presenter.get_trend_data(start_date=start_date, end_date=end_date)
        except NotFoundError:
            raise Http404

        # add the enrollment data for the page
        context['js_data']['course']['enrollmentTrends'] = data
        context.update({
            'page_data': json.dumps(context['js_data']),
            'summary': summary,
            'tooltips': tooltips,
        })

        return context


class EnrollmentGeographyView(EnrollmentTemplateView):
    template_name = 'courses/enrollment_geography.html'
    page_title = 'Enrollment Geography'
    page_name = 'enrollment_geography'
    active_secondary_nav_item = 'Geography'

    def get_context_data(self, **kwargs):
        context = super(EnrollmentGeographyView, self).get_context_data(**kwargs)

        presenter = CourseEnrollmentPresenter(self.course_id)

        try:
            data, last_update = presenter.get_geography_data()
        except NotFoundError:
            raise Http404

        context['js_data']['course']['enrollmentByCountry'] = data
        context['js_data']['course']['enrollmentByCountryUpdateDate'] = get_formatted_date(last_update)
        context.update({
            'page_data': json.dumps(context['js_data']),
        })

        return context


class EngagementContentView(EngagementTemplateView):
    template_name = 'courses/engagement_content.html'
    page_title = 'Engagement Content'
    page_name = 'engagement_content'
    active_secondary_nav_item = 'Content'

    # pylint: disable=line-too-long
    def get_context_data(self, **kwargs):
        context = super(EngagementContentView, self).get_context_data(**kwargs)

        tooltips = {
            'all_activity_summary': 'Students who initiated an action.',
            'posted_forum_summary': 'Students who created a post, responded to a post, or made a comment in any discussion.',
            'attempted_problem_summary': 'Students who answered any question.',
            'played_video_summary': 'Students who started watching any video.',
        }

        presenter = CourseEngagementPresenter()
        summary = presenter.get_summary(self.course_id)

        summary['week_of_activity'] = get_formatted_date_time(summary['interval_end'])

        context.update({
            'tooltips': tooltips,
            'summary': summary,
            'page_data': json.dumps(context['js_data']),
        })

        return context


class OverviewView(CourseTemplateView):
    template_name = 'courses/overview.html'
    page_title = 'Overview'
    page_name = 'overview'
    active_primary_nav_item = 'Overview'


class PerformanceView(CourseTemplateView):
    template_name = 'courses/performance.html'
    page_title = 'Performance'
    page_name = 'performance'
    active_primary_nav_item = 'Performance'


class CourseEnrollmentByCountryCSV(CSVResponseMixin, CourseView):
    def get_context_data(self, **kwargs):
        context = super(CourseEnrollmentByCountryCSV, self).get_context_data(
            **kwargs)

        context.update({
            'data': self.course.enrollment(demographic.LOCATION,
                                           data_format=data_format.CSV),
            'filename': '{0}_enrollment_by_country.csv'.format(self.course_id)
        })

        return context


class CourseEnrollmentCSV(CSVResponseMixin, CourseView):
    def get_context_data(self, **kwargs):
        context = super(CourseEnrollmentCSV, self).get_context_data(**kwargs)
        end_date = datetime.date.today().strftime(Client.DATE_FORMAT)

        context.update({
            'data': self.course.enrollment(data_format=data_format.CSV,
                                           end_date=end_date),
            'filename': '{0}_enrollment.csv'.format(self.course_id)
        })

        return context


class CourseHome(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        course_id = kwargs['course_id']
        return reverse('courses:enrollment_activity', kwargs={'course_id': course_id})


class CourseIndex(LoginRequiredMixin, TemplateView):
    template_name = 'courses/index.html'

    def get_context_data(self, **kwargs):
        context = super(CourseIndex, self).get_context_data(**kwargs)

        courses = permissions.get_user_course_permissions(self.request.user)

        if not courses:
            # The user is probably not a course administrator and should
            # not be using this application.
            raise PermissionDenied

        context['courses'] = courses

        return context
