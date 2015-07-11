# pylint: disable=no-value-for-parameter

from django.conf.urls import url, patterns

from users import views

urlpatterns = patterns(
    '',
    url(r'^$', views.UserListView.as_view(), name='list'),
    url(r'^(?P<user_id>\d+)/$', views.UserProfileView.as_view(), name='profile'),
)
