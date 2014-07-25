import json
import datetime

from django.conf import settings

from django.shortcuts import render
from django.http import Http404, HttpResponse

from analyticsclient import data_format, demographic
from analyticsclient.client import Client
from analyticsclient.exceptions import NotFoundError
from django.views.generic import View
from django.views.generic.base import ContextMixin

from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter
from courses.utils import get_formatted_date, get_formatted_date_time


class CourseView(ContextMixin, View):
    client = Client(base_url=settings.DATA_API_URL, auth_token=settings.DATA_API_AUTH_TOKEN, timeout=5)
    course = None
    course_id = None

    def render_to_response(self, context, **response_kwargs):
        raise NotImplementedError

    def get(self, _request, *_args, **kwargs):
        self.course_id = kwargs['course_id']
        self.course = self.client.courses(self.course_id)

        try:
            return self.render_to_response(context=self.get_context_data())
        except NotFoundError:
            raise Http404


class CSVResponseMixin(object):
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(context['data'], content_type='text/csv', **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(context['filename'])
        return response


class JSONResponseMixin(object):
    def render_to_response(self, context, **response_kwargs):
        content = json.dumps(context['data'])
        return HttpResponse(content, content_type='application/json', **response_kwargs)


def get_default_data(course_id):
    """
    Returns default data for the pages.

    TODO: we would ideally get this from the DB, but for now lets stub some data
    """
    return {
        'user_name': 'Ed Xavier',
        'course_number': 'MITx 7.3423',
        'course_title': 'Introduction to Awesomeness',
        'course_id': course_id,
    }


def enrollment(request, course_id):
    """ Renders the Enrollment page. """

    tooltips = {
        'current_enrollment': 'Students enrolled in course.',
        'enrollment_change_last_1_days': 'Change in enrollment for the last full day (00:00-23:59 UTC).',
        'enrollment_change_last_7_days': 'Change in enrollment during the last 7 days (through 23:59 UTC).',
        'enrollment_change_last_30_days': 'Change in enrollment during the last 30 days (through 23:59 UTC).'
    }

    presenter = CourseEnrollmentPresenter(course_id)

    try:
        summary = presenter.get_summary()
        end_date = summary['date']
        start_date = end_date - datetime.timedelta(days=60)
        end_date = end_date + datetime.timedelta(days=1)
        data = presenter.get_data(start_date=start_date, end_date=end_date)
    except NotFoundError:
        raise Http404

    context = get_default_data(course_id)

    js_data = {
        'courseId': course_id,
        'enrollmentTrends': data
    }

    context.update({
        'page_data': json.dumps(js_data),
        'page_title': 'Enrollment',
        'summary': summary,
        'tooltips': tooltips,
    })

    return render(request, 'courses/enrollment.html', context)


def overview(request, course_id):
    """
    Renders the Overview page.
    """
    context = get_default_data(course_id)
    context['page_title'] = 'Overview'
    return render(request, 'courses/overview.html', context)


# pylint: disable=line-too-long
def engagement(request, course_id):
    """
    Renders the Engagement page.
    """
    # these are the tooltips displayed in the page
    tooltips = {
        'all_activity_summary': 'Students who initiated an action.',
        'posted_forum_summary': 'Students who created a post, responded to a post, or made a comment in any discussion.',
        'attempted_problem_summary': 'Students who answered any question.',
        'played_video_summary': 'Students who started watching any video.',
    }

    try:
        presenter = CourseEngagementPresenter()
        summary = presenter.get_summary(course_id)
    except NotFoundError:
        # Raise a 404 if the course is not found by the API
        raise Http404

    summary['week_of_activity'] = get_formatted_date_time(summary['interval_end'])

    context = get_default_data(course_id)
    context.update({
        'page_title': 'Engagement',
        'tooltips': tooltips,
        'summary': summary,
        'page_data': json.dumps({'courseId': str(course_id)})
    })

    return render(request, 'courses/engagement.html', context)


def performance(request, course_id):
    """
    Renders the Performance page.
    """
    context = get_default_data(course_id)
    context['page_title'] = 'Performance'
    return render(request, 'courses/performance.html', context)


class CourseEnrollmentByCountryJSON(JSONResponseMixin, CourseView):
    def get_context_data(self, **kwargs):
        context = super(CourseEnrollmentByCountryJSON, self).get_context_data(**kwargs)

        api_response = self.course.enrollment(demographic.LOCATION)
        data = {'date': None, 'data': []}

        if api_response:
            start_date = api_response[0]['date']
            api_data = [{'country_code': datum['country']['code'],
                         'country_name': datum['country']['name'],
                         'value': datum['count']} for datum in api_response]

            data.update({'date': get_formatted_date(start_date), 'data': api_data})

        context['data'] = data

        return context


class CourseEnrollmentByCountryCSV(CSVResponseMixin, CourseView):
    def get_context_data(self, **kwargs):
        context = super(CourseEnrollmentByCountryCSV, self).get_context_data(**kwargs)

        context.update({
            'data': self.course.enrollment(demographic.LOCATION, data_format=data_format.CSV),
            'filename': '{0}_enrollment_by_country.csv'.format(self.course_id)
        })

        return context


class CourseEnrollmentCSV(CSVResponseMixin, CourseView):
    def get_context_data(self, **kwargs):
        context = super(CourseEnrollmentCSV, self).get_context_data(**kwargs)
        end_date = datetime.date.today().strftime(Client.DATE_FORMAT)

        context.update({
            'data': self.course.enrollment(data_format=data_format.CSV, end_date=end_date),
            'filename': '{0}_enrollment.csv'.format(self.course_id)
        })

        return context
