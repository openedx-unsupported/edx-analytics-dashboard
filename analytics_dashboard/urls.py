# pylint: disable=line-too-long,no-value-for-parameter
import os

from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views import defaults
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog
from django.contrib.staticfiles import views as static_views

# pylint suggests importing analytics_dashboard.core, which causes errors in our AMI
# pylint: disable=relative-import
from core import views


admin.autodiscover()

urlpatterns = [
    url(r'^$', views.LandingView.as_view(), name='landing'),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=['core', 'courses']), name='javascript-catalog'),
    url(r'^status/$', views.status, name='status'),
    url(r'^health/$', views.health, name='health'),
    url(r'^courses/', include('courses.urls')),
    url(r'^admin/', admin.site.urls),
    # TODO: the namespace arg is deprecated, but python-social-auth urls.py doesn't specify app_name so we are stuck
    # using namespace. Once python-social-auth is updated to fix that, remove the namespace arg.
    url('', include('social_django.urls', namespace='social')),
    url(r'^accounts/login/$',
        RedirectView.as_view(url=reverse_lazy('social:begin', args=['edx-oidc']), permanent=False, query_string=True),
        name='login'),
    url(r'^accounts/logout/$', views.InsightsLogoutView.as_view(), name='logout'),
    url(r'^accounts/logout_then_login/$', views.insights_logout_then_login, name='logout_then_login'),
    url(r'^test/auto_auth/$', views.AutoAuth.as_view(), name='auto_auth'),
    url(r'^announcements/', include('pinax.announcements.urls', namespace='pinax_announcements')),
]

urlpatterns += [
    url(r'^api/learner_analytics/', include('learner_analytics_api.urls'))
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
        import debug_toolbar  # pylint: disable=import-error, wrong-import-position, wrong-import-order

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]

    if settings.ENABLE_INSECURE_STATIC_FILES:
        urlpatterns += [
            url(r'^static/(?P<path>.*)$', static_views.serve),
        ]
