from rest_framework import generics

from django.http import HttpResponse

from .utils import LearnerAPIClient


# LEARNER API VIEWS
# TODO: caching?
# TODO: authenticate? or is it just already done?
class BaseLearnerApiView(generics.RetrieveAPIView):
    def __init__(self, *args, **kwargs):
        super(BaseLearnerApiView, self).__init__(*args, **kwargs)
        self.client = LearnerAPIClient()


class LearnerDetailView(BaseLearnerApiView):
    def get(self, request, username, **kwargs):
        kwargs.update(request.query_params)
        return HttpResponse(self.client.learners(username).get(**kwargs))


class LearnerListView(BaseLearnerApiView):
    def get(self, request, **kwargs):
        kwargs.update(request.query_params)
        return HttpResponse(self.client.learners.get(**kwargs))


class EngagementTimelinesView(BaseLearnerApiView):
    def get(self, request, username, **kwargs):
        kwargs.update(request.query_params)
        return HttpResponse(self.client.engagement_timelines(username).get(**kwargs))


class CourseLearnerMetadata(BaseLearnerApiView):
    def get(self, request, course_id, **kwargs):
        kwargs.update(request.query_params)
        return HttpResponse(self.client.course_learner_metadata(course_id).get(**kwargs))
