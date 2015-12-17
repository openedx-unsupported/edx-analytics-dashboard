from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    '',
    url(r'^v0/', include('learner_analytics_api.v0.urls', namespace='v0'))
)
