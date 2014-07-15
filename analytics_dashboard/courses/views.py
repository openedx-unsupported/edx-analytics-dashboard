import json

from django.shortcuts import render
from django.http import Http404

from analyticsclient.exceptions import ClientError

from courses.models import StudentEngagement
from courses.utils import get_formatted_date

def get_default_data(course_id):
    """
    Returns default data for the pages.

    TODO: we would ideally get this from the DB, but for now lets stub some data
    """
    page_data = {
        'courseId': str(course_id),
    }
    return {
        'user_name': 'Ed Xavier',
        'course_number': 'MITx 7.3423',
        'course_title': 'Introduction to Awesomeness',
        'course_id': course_id,
        'page_data': json.dumps(page_data)
    }

def enrollment(request, course_id):
    """
    Renders the Enrollment page.
    """
    context = get_default_data(course_id)
    context['page_title'] = 'Enrollment'
    # TODO: this is just to test out the tooltip
    context['total_enrollment_tooltip'] = "And here's some amazing content. " \
                                          "It's very engaging. Right?"
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
        'all_activity_summary': '''
            Students who initiated an action.
            '''.strip(),
        'posted_forum_summary': '''
            Students who created a post, responded to a post, or made a comment in any discussion.
            '''.strip(),
        'attempted_problem_summary': '''
            Students who answered any question.
            '''.strip(),
        'played_video_summary': '''
            Students who started watching any video.
            '''.strip(),
    }

    # get the student engagement summary information or throw a 404
    student_engagement = StudentEngagement()
    try:
        # get the summary information
        summary = student_engagement.get_summary(course_id)
    except ClientError:
        # TODO: this is currently a 404 for all failed requests.  We'd like
        # to put a 500 if there is a server error (not an invalid course ID).
        raise Http404

    summary['week_of_activity'] = get_formatted_date(summary['interval_end'])

    context = get_default_data(course_id)
    context['page_title'] = 'Engagement'
    context['tooltips'] = tooltips
    context['summary'] = summary
    return render(request, 'courses/engagement.html', context)


def performance(request, course_id):
    """
    Renders the Performance page.
    """
    context = get_default_data(course_id)
    context['page_title'] = 'Performance'
    return render(request, 'courses/performance.html', context)
