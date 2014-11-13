# pylint: disable=line-too-long,no-value-for-parameter
import os

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from analytics_dashboard import views


admin.autodiscover()

js_info_dict = {
    'packages': ('analytics_dashboard', 'courses',),
}

urlpatterns = patterns(
    '',
    url(r'^$', RedirectView.as_view(url=reverse_lazy('courses:index')), name='home'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^status/$', views.status, name='status'),
    url(r'^health/$', views.health, name='health'),
    url(r'^courses/', include('courses.urls', namespace='courses')),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^accounts/login/$',
        RedirectView.as_view(url=reverse_lazy('social:begin', args=['edx-oidc']), permanent=False, query_string=True),
        name='login'),
    url(r'^accounts/logout/$', views.logout, name='logout'),
    url(r'^accounts/logout_then_login/$', views.logout_then_login, name='logout_then_login'),
    url(r'^test/auto_auth/$', views.AutoAuth.as_view(), name='auto_auth'),
    url(r'^auth/error/$', 'django.views.defaults.server_error', {'template_name': 'auth_error.html'},
        name='auth_error'),
    url(r'^announcements/', include('announcements.urls')),
)

if settings.DEBUG:  # pragma: no cover
    urlpatterns += patterns(
        '',
        url(r'^403/$', 'django.views.defaults.permission_denied'),
        url(r'^404/$', 'django.views.defaults.page_not_found'),
        url(r'^500/$', 'django.views.defaults.server_error'),
    )

    if os.environ.get('ENABLE_DJANGO_TOOLBAR', False):
        import debug_toolbar  # pylint: disable=import-error

        urlpatterns += patterns(
            '',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )
