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
