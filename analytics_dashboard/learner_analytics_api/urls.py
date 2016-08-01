from django.conf.urls import url, include

app_name = 'learner_analytics_api'
urlpatterns = [
    url(r'^v0/', include('learner_analytics_api.v0.urls'))
]
