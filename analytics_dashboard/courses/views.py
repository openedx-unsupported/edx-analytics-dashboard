import json
import datetime

from django.shortcuts import render
from django.http import Http404

from analyticsclient.exceptions import NotFoundError

from courses.presenters import StudentEngagement, StudentEnrollment
from courses.utils import get_formatted_date, get_formatted_date_time, \
    get_formatted_summary_number, strip_tooltips

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
    """
    Renders the Enrollment page.
    """
    tooltips = strip_tooltips({
        'total_enrollment': '''
            Students enrolled in course.
            ''',
        'enrollment_change_yesterday': '''
            Change in enrollment for the past day (through yesterday).
            ''',
        'enrollment_change_last_7_days': '''
            Change in enrollment during the past week (7 days ending yesterday).
            ''',
        'enrollment_change_last_30_days': '''
            Change in enrollment over the past month (30 days ending yesterday).
            '''
    })

    student_enrollment = StudentEnrollment()

    try:
        summary = student_enrollment.get_summary(course_id)
        # use the last updated date as the end date for our trendline
        last_update_date = datetime.datetime.strptime(
            summary['date_end'], StudentEnrollment.DATE_FORMAT)
        trends = student_enrollment.get_enrollment_trend(course_id,
                                                         last_update_date, 60)
    except NotFoundError:
        raise Http404

    display_summary = {
        'last_update': get_formatted_date(summary['date_end'])
    }

    # lets turn all "None" summary values into n/a
    summary_fields = ['total_enrollment', 'enrollment_change_yesterday',
                      'enrollment_change_last_7_days',
                      'enrollment_change_last_30_days']
    for field in summary_fields:
        display_summary[field] = get_formatted_summary_number(summary[field])

    # add a '+' to the summary trend if it's positive
    for field in summary_fields[1:len(summary_fields)]:
        if summary[field] is not None and summary[field] > 0:
            display_summary[field] = '+' + display_summary[field]

    context = get_default_data(course_id)

    # record the data that we'd like to return to the page for javascript
    # consumption
    page_data = {
        'courseId': course_id,
        'enrollmentTrends': trends
    }
    context['page_data'] = json.dumps(page_data)

    context['page_title'] = 'Enrollment'
    context['summary'] = display_summary
    context['tooltips'] = tooltips
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
    tooltips = strip_tooltips({
        'all_activity_summary': '''
            Students who initiated an action.
            '''.replace('\n', ''),
        'posted_forum_summary': '''
            Students who created a post, responded to a post, or made a comment
            in any discussion.
            '''.replace('\n', ''),
        'attempted_problem_summary': '''
            Students who answered any question.
            '''.replace('\n', ''),
        'played_video_summary': '''
            Students who started watching any video.
            '''.replace('\n', ''),
    })

    # get the student engagement summary information or throw a 404
    student_engagement = StudentEngagement()
    try:
        # get the summary information
        summary = student_engagement.get_summary(course_id)
    except NotFoundError:
        raise Http404

    summary['week_of_activity'] = get_formatted_date_time(
        summary['interval_end'])

    context = get_default_data(course_id)
    context['page_title'] = 'Engagement'
    context['tooltips'] = tooltips
    context['summary'] = summary

    # page data is passed to javascript
    page_data = {
        'courseId': str(course_id),
    }
    context['page_data'] = json.dumps(page_data)

    return render(request, 'courses/engagement.html', context)


def performance(request, course_id):
    """
    Renders the Performance page.
    """
    context = get_default_data(course_id)
    context['page_title'] = 'Performance'
    return render(request, 'courses/performance.html', context)
