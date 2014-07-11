import time
import json

from django.shortcuts import render
from django.http import Http404

from models import StudentEngagement


# TODO: we would ideally get this from the DB, but for now lets stub some data
def get_default_data(course_id):
    page_data = {
        'courseId': str(course_id),
    }
    # we would ideally get this from the DB, but for now lets stub some data
    return {
        'user_name': 'Ed Xavier',
        'course_number': 'MITx 7.3423',
        'course_title': 'Introduction to Awesomeness',
        'course_id': course_id,
        'page_data': json.dumps(page_data)
    }


def enrollment(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Enrollment'
    context['total_enrollment_tooltip'] = "And here's some amazing content. It's very engaging. Right?"
    return render(request, 'courses/enrollment.html', context)


def overview(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Overview'
    return render(request, 'courses/overview.html', context)


def engagement(request, course_id):
    # these are the tooltips displayed in the page
    tooltips = {
        'all_activity_summary': '''
            The number of unique users who performed any action within the course.
            ''',
        'posted_forum_summary': '''
            The number of unique users who created a new post, responded to a post, or submitted a comment on any forum
            in the course.
            ''',
        'attempted_problem_summary': '''
            The number of unique users who answered any question in the course.
            ''',
        'played_video_summary': '''
            The number of unique users who started watching any video in the course.
            ''',
    }

    # get the student engagement summary information or throw a 404
    studentEngagement = StudentEngagement()
    try:
        # get the summary information
        summary = studentEngagement.get_summary(course_id)

        # make the date human readable
        struct_time = time.strptime(summary['interval_start'], "%Y-%m-%dT%H:%M:%SZ")
        summary['week_of_activity'] = time.strftime('%B %d, %Y', struct_time)
    except:
        raise Http404

    context = get_default_data(course_id)
    context['page_title'] = 'Engagement'
    context['tooltips'] = tooltips
    context['summary'] = summary
    return render(request, 'courses/engagement.html', context)


def performance(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Performance'
    return render(request, 'courses/performance.html', context)
