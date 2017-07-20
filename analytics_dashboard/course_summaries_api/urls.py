from django.conf.urls import url, include

app_name = 'course_summaries_api'
urlpatterns = [
    url(r'^v0/', include('course_summaries_api.v0.urls'))
]
