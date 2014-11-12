import urllib
from django.core.cache import cache
import urllib

from django.core.cache import cache
import requests


class Course(object):
    def __init__(self, url, key):
        self.url = url.strip('/')
        self.api_key = key

    def _get(self, path):
        uri = u'{0}/{1}'.format(self.url, path)
        headers = {u'X-Edx-Api-Key': self.api_key}

        return requests.get(uri, headers=headers).json()

    def course_detail(self, course_id, depth=0, content_type=None):
        """
        Retrieve detail for the given course up to the specified tree depth.
        """
        qs_params = {u'depth': depth, u'include_fields': u'graded,format'}
        if content_type:
            qs_params[u'type'] = content_type

        path = u'courses/{course_id}?{qs}'.format(course_id=course_id, qs=urllib.urlencode(qs_params))
        detail = cache.get(path)

        if not detail:
            detail = self._get(path)
        cache.set(path, detail)

        return detail

    def _get_graded_items(self, items):
        """
        Given a list of nested items, return a flat list of graded items.
        """
        graded_items = []

        for item in items:
            graded = self._filter_graded(item)
            if graded:
                graded_items += graded

        return graded_items

    def _filter_graded(self, item):
        # If the item is graded, return the item.
        if item.get(u'graded', False):
            return [item]

        # If the item is not graded, check its children.
        children = []
        for child in item.get(u'children', []):
            graded_children = self._filter_graded(child)

            if graded_children:
                children += graded_children

        return children

    def _get_graded_content(self, course_id, graded_content_type=None):
        content = self.course_detail(course_id, 3)[u'content']
        content = self._get_graded_items(content)

        if graded_content_type:
            graded_content_type = graded_content_type.lower()
            content = [item for item in content if (item.get(u'format') or '').lower() == graded_content_type]

        return content

    def homeworks(self, course_id):
        """
        Retrieve all homeworks for a given course.
        """
        return self._get_graded_content(course_id, u'Homework')

    def exams(self, course_id):
        """
        Retrieve all exams for a given course.
        """
        return self._get_graded_content(course_id, u'Exam')
