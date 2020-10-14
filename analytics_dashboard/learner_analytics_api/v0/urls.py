from django.conf import settings
from django.conf.urls import url

from . import views

USERNAME_PATTERN = r'(?P<username>.+)'

app_name = 'v0'
urlpatterns = [
    url(fr'^learners/{USERNAME_PATTERN}/$', views.LearnerDetailView.as_view(), name='LearnerDetail'),
    url(r'^learners/$', views.LearnerListView.as_view(), name='LearnerList'),
    url(r'^learners.csv$', views.LearnerListCSV.as_view(), name='LearnerListCSV'),
    url(fr'^engagement_timelines/{USERNAME_PATTERN}/$',
        views.EngagementTimelinesView.as_view(),
        name='EngagementTimeline'),
    url(fr'^course_learner_metadata/{settings.COURSE_ID_PATTERN}/$',
        views.CourseLearnerMetadataView.as_view(),
        name='CourseMetadata'),
]
