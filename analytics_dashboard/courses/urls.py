from django.conf.urls import patterns, url

from courses import views

urlpatterns = patterns('',
    # ex: /courses/5/
    url(r'^(?P<course_id>\d+)/$', views.analytics, name='analytics'),
)