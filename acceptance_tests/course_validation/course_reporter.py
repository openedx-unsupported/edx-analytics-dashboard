from analyticsclient.constants import demographic
from analyticsclient.exceptions import ClientError

from acceptance_tests.course_validation import DASHBOARD_SERVER_URL


COURSE_PAGES = ['enrollment/activity', 'enrollment/geography', 'engagement/content']
API_REPORT_KEYS = ['api_enrollment_activity', 'api_enrollment_geography', 'api_activity']


class CourseReporter(object):
    course = None
    course_id = None

    def __init__(self, course, http_client):
        self.course = course
        self.course_id = course.course_id
        self.http_client = http_client

    def _http_status(self, url):
        r = self.http_client.get(url)
        return r.status_code

    def _build_course_url(self, path):
        return '{0}/courses/{1}/{2}/'.format(DASHBOARD_SERVER_URL, self.course_id, path)

    def has_enrollment_activity(self):
        try:
            self.course.enrollment()
            return True
        except ClientError as e:
            return False

    def has_enrollment_geography(self):
        try:
            self.course.enrollment(demographic.LOCATION)
            return True
        except ClientError:
            return False

    def has_engagement_activity(self):
        try:
            self.course.activity()
            return True
        except ClientError:
            return False

    def report(self):
        report = {
            'course_id': self.course_id
        }

        # Check that the pages load
        for page in COURSE_PAGES:
            report[page] = self._http_status(self._build_course_url(page))

        # Check API for data
        report['api_enrollment_activity'] = self.has_enrollment_activity()
        report['api_enrollment_geography'] = self.has_enrollment_geography()
        report['api_activity'] = self.has_engagement_activity()

        return report
