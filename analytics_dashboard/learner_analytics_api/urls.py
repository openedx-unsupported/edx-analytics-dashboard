from django.conf.urls import url, include

urlpatterns = [
    url(r'^v0/', include('learner_analytics_api.v0.urls', namespace='v0'))
]
