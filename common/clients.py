import logging

from edx_rest_api_client.client import EdxRestApiClient
from edx_rest_api_client.exceptions import HttpClientError


logger = logging.getLogger(__name__)


class CourseStructureApiClient(EdxRestApiClient):
    """
    This class is a sub-class of the edX Rest API Client
    (https://github.com/edx/edx-rest-api-client).

    Details about the API itself can be found at
    https://openedx.atlassian.net/wiki/display/AN/Course+Structure+API.
    """
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, url, access_token, timeout):
        super(CourseStructureApiClient, self).__init__(url, oauth_access_token=access_token, timeout=timeout)

    @property
    def all_courses(self):
        courses = []
        page = 1

        while page:
            try:
                logger.debug('Retrieving page %d of course info...', page)
                response = self.courses.get(page=page, page_size=100)
                course_details = response['results']

                courses += course_details

                if response['next']:
                    page += 1
                else:
                    page = None
                    logger.debug('Completed retrieval of course info. Retrieved info for %d courses.', len(courses))
            except HttpClientError as e:
                logger.error("Unable to retrieve course data: %s", e)
                page = None
                break

        return courses
