from django.conf.urls import url

import views

app_name = 'course_summaries_api'
urlpatterns = [
    url(r'^course_summaries/$', views.CourseSummariesAPIView.as_view())
]
