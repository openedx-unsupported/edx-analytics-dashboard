from django.conf.urls import patterns, include, url

from courses import views

urlpatterns = [
    # ex. courses/edX/DemoX/Demo_Course/
    url(r'^(?P<course_id>(\w+/){2}\w+)/',
        include([
            url(r'^enrollment/$', views.enrollment),
            url(r'^engagement/$', views.engagement),
            url(r'^performance/$', views.performance),
            url(r'^overview/$', views.overview),
        ])
    )
]