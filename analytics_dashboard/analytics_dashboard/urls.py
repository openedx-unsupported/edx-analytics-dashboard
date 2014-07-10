from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from analytics_dashboard import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^status/$', views.status, name='status'),
    url(r'^courses/', include('courses.urls', namespace="courses")),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
