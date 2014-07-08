from django.conf.urls import url, patterns

from courses import views
import re

COURSE_URLS = [
    ('enrollment', views.enrollment),
    ('engagement', views.engagement),
    ('performance', views.performance),
    ('overview', views.overview),
]

urlpatterns = []

for name, view in COURSE_URLS:
    urlpatterns += patterns('', url(r'^(?P<course_id>(\w+/){2}\w+)/' + re.escape(name) + r'/$', view, name=name))

