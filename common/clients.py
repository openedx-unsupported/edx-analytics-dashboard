import logging
from urllib.parse import urljoin

from django.conf import settings
from edx_rest_api_client.client import OAuthAPIClient
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


class CourseStructureApiClient(OAuthAPIClient):
    """
    This class is a sub-class of the edX Rest API Client
    (https://github.com/openedx/edx-rest-api-client).

    Details about the API itself can be found at
    https://openedx.atlassian.net/wiki/display/AN/Course+Structure+API.
    """
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    @property
    def all_courses(self):
        courses = []
        page = 1

        while page:
            try:
                logger.debug('Retrieving page %d of course info...', page)
                response = self.get(
                    urljoin(settings.COURSE_API_URL + '/', 'courses/'),
                    params={
                        'page': page,
                        'page_size': 100
                    }
                ).json()
                course_details = response['results']

                courses += course_details

                if response['pagination']['next']:
                    page += 1
                else:
                    page = None
                    logger.debug('Completed retrieval of course info. Retrieved info for %d courses.', len(courses))
            except (KeyError, HTTPError) as e:
                logger.error("Unable to retrieve course data: %s", e)
                page = None
                break

        return courses

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        response = super().request(method, url, **kwargs)
        response.raise_for_status()
        return response
