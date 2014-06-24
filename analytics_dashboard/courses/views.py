from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from models import Course

def analytics(request, course_id):
    # we would ideally get this from the DB, but for now lets stub some data
    context = {'user_name': 'Ed Xavier',
               'course_number': 'MITx 7.3423',
               'course_title': 'Introduction to Awesomeness'
    }
    return render(request, 'courses/analytics.html', context)
