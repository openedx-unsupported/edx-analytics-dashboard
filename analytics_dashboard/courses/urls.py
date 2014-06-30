from django.conf.urls import patterns, include, url

from courses import views

urlpatterns = [
    url(r'^(?P<course_id>\d+)/', include([
        url(r'^enrollment/$', views.enrollment),
        url(r'^engagement/$', views.engagement),
        url(r'^performance/$', views.performance),
        url(r'^overview/$', views.overview),
    ]))

    # , views.analytics, name='analytics'),
    # url(r'^(?P<course_id>\d+\[^/]+)(/)?enrollment/$', views.enrollment, name='enrollment'),
    # ex: /courses/5/
    # url(r'^(?P<course_id>\d+)/$', views.analytics, name='analytics'),
    # url(r'^(?P<course_id>\d+\[^/]+)(/)?enrollment/$', views.enrollment, name='enrollment'),

]