import slumber

from common.auth import BearerAuth


class CourseStructureApiClient(slumber.API):
    """
    Course Structure API Client

    This class is a sub-class slumber.API (http://slumber.readthedocs.org/en/latest/). Details
    about the API itself can be found at https://openedx.atlassian.net/wiki/display/AN/Course+Structure+API.
    """
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, url, access_token):
        super(CourseStructureApiClient, self).__init__(url, auth=BearerAuth(access_token))
