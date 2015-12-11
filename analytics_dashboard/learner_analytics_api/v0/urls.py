from django.conf import settings
from django.conf.urls import patterns, url

from . import views


USERNAME_PATTERN = r'(?P<username>.+)'

urlpatterns = patterns(
    '',
    url(r'^learners/{}/$'.format(USERNAME_PATTERN), views.LearnerDetailView.as_view()),
    url(r'^learners/$', views.LearnerListView.as_view()),
    url(r'^engagement_timelines/{}/$'.format(USERNAME_PATTERN), views.EngagementTimelinesView.as_view()),
    url(r'^course_learner_metadata/{}/$'.format(settings.COURSE_ID_PATTERN), views.CourseLearnerMetadataView.as_view()),
)
