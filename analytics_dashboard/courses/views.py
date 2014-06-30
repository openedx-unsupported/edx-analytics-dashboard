from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import json

from models import Course

# we would ideally get this from the DB, but for now lets stub some data
def get_default_data(course_id):
    page_data = {
        'name': 'Dennis',
        'courseId': str(course_id),
    }
    # we would ideally get this from the DB, but for now lets stub some data
    return {'user_name': 'Ed Xavier',
               'course_number': 'MITx 7.3423',
               'course_title': 'Introduction to Awesomeness',
               'page_data': json.dumps(page_data)
    }

def enrollment(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Enrollment'
    return render(request, 'courses/enrollment.html', context)

def overview(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Overview'
    return render(request, 'courses/overview.html', context)

def engagement(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Engagement'
    return render(request, 'courses/engagement.html', context)

def performance(request, course_id):
    context = get_default_data(course_id)
    context['page_title'] = 'Performance'
    return render(request, 'courses/performance.html', context)
