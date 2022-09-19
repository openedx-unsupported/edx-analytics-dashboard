import os

from auth_backends.urls import oauth2_urlpatterns
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles import views as static_views
from django.views import defaults
from django.views.i18n import JavaScriptCatalog

from analytics_dashboard.core import views

admin.autodiscover()

# NOTE 1: Add our logout override first to ensure it is registered by Django as the actual logout view.
# NOTE 2: These same patterns are used for rest_framework's browseable API authentication links.
AUTH_URLS = [
    url(r'^logout/$', views.InsightsLogoutView.as_view(), name='logout'),
    url(r'^logout_then_login/$', views.insights_logout_then_login, name='logout_then_login'),
] + oauth2_urlpatterns

urlpatterns = AUTH_URLS + [
    url(r'^$', views.LandingView.as_view(), name='landing'),
    url(
        r'^jsi18n/$',
        JavaScriptCatalog.as_view(
            packages=['analytics_dashboard.core', 'analytics_dashboard.courses']
        ),
        name='javascript-catalog',
    ),
    url(r'^status/$', views.status, name='status'),
    url(r'^health/$', views.health, name='health'),
    url(r'^courses/', include('courses.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include((AUTH_URLS, 'auth_urls'), namespace='rest_framework')),
    url(r'^test/auto_auth/$', views.AutoAuth.as_view(), name='auto_auth'),
    url(r'^announcements/', include('pinax.announcements.urls', namespace='pinax_announcements')),
]


def debug_page_not_found(request):
    return defaults.page_not_found(request, AttributeError('foobar'))


def debug_permission_denied(request):
    return defaults.permission_denied(request, AttributeError('foobar'))


if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        url(r'^403/$', debug_permission_denied),
        url(r'^404/$', debug_page_not_found),
        url(r'^500/$', defaults.server_error),
        url(r'^503/$', views.ServiceUnavailableView.as_view()),
    ]

    if os.environ.get('ENABLE_DJANGO_TOOLBAR', False):
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]

    if settings.ENABLE_INSECURE_STATIC_FILES:
        urlpatterns += [
            url(r'^static/(?P<path>.*)$', static_views.serve),
        ]
