import json
import datetime

from django.shortcuts import render
from django.http import Http404

from analyticsclient.exceptions import NotFoundError
from courses.presenters import CourseEngagementPresenter, CourseEnrollmentPresenter
from courses.utils import get_formatted_date_time


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
        'enrollment_change_last_1_days': 'Change in enrollment for the past day (through yesterday).',
        'enrollment_change_last_7_days': 'Change in enrollment during the past week (7 days ending yesterday).',
        'enrollment_change_last_30_days': 'Change in enrollment over the past month (30 days ending yesterday).'
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
