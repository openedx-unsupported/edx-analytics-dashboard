# pylint: disable=no-value-for-parameter

from django.conf.urls import url, patterns

from users import views

urlpatterns = patterns(
    '',
    url(r'^$', views.UserListView.as_view(), name='list'),
    url(r'^(?P<username>[^/]+)/$', views.UserProfileView.as_view(), name='profile'),
    url(r'^(?P<username>[^/]+)/problems/$', views.UserProblemDataView.as_view(), name='problems')
)
