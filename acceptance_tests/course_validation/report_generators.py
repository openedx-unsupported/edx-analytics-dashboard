import datetime
import logging
import traceback
from os.path import join

from analyticsclient.client import Client
import requests
from selenium import webdriver
from slugify import slugify

from acceptance_tests.course_validation import DASHBOARD_SERVER_URL, COURSE_API_URL, COURSE_API_KEY, API_SERVER_URL, \
    API_AUTH_TOKEN, ENABLE_AUTO_AUTH, LMS_URL, LMS_USERNAME, LMS_PASSWORD, BASIC_AUTH_CREDENTIALS
from common.clients import CourseStructureApiClient
from common.course_structure import CourseStructure


logger = logging.getLogger(__name__)


class ReportGeneratorBase(object):
    REPORT_NAME = None
    course_id = None

    def __init__(self, course_id, http_cookies=None):
        self.course_id = course_id
        self.analytics_api_client = Client(base_url=API_SERVER_URL, auth_token=API_AUTH_TOKEN, timeout=1000)
        self.course_api_client = CourseStructureApiClient(COURSE_API_URL, COURSE_API_KEY)
        self.http_client = requests.Session()
        self.http_client.cookies = http_cookies

    def get_http_status_and_load_time(self, url):
        r = self.http_client.get(url)
        elapsed = None

        if r.elapsed:
            elapsed = r.elapsed.total_seconds()

        return r.status_code, elapsed

    def build_course_path(self, path):
        path = path.strip('/')
        return '/courses/{}/{}/'.format(self.course_id, path)

    def get_dashboard_url(self, path):
        path = path.strip('/')
        return '{}/{}/'.format(DASHBOARD_SERVER_URL, path)

    def generate_report(self):
        """
        Generates a report for a course.

        This method should return a tuple--(valid, report)--where valid is a boolean indicating if the course meets
        the reporter's conditions for validity, and report is a JSON-serializable dict containing the output of the
        analysis.
        """
        raise NotImplementedError


# TODO Update this class to inherit from ReporterBase
#
# COURSE_PAGES = ['enrollment/activity', 'enrollment/geography', 'engagement/content', 'performance/graded_content']
# API_REPORT_KEYS = ['api_enrollment_activity', 'api_enrollment_geography', 'api_activity', 'api_problems']
#
# class CourseReporter(object):
# course = None
# course_id = None
#
# def __init__(self, course, logger, cookies=None):
#         self.course = course
#         self.course_id = course.course_id
#         self.http_client = requests.Session()
#         self.http_client.cookies = cookies
#         self.course_pages = COURSE_PAGES
#         self.logger = logger
#
#     def _http_status(self, url):
#         r = self.http_client.get(url)
#         return r.status_code
#
#     def _build_course_url(self, path):
#         path = path.strip('/')
#         return '{0}/courses/{1}/{2}/'.format(DASHBOARD_SERVER_URL, self.course_id, path)
#
#     def has_enrollment_activity(self):
#         try:
#             self.course.enrollment()
#             return True
#         except ClientError:
#             return False
#
#     def has_enrollment_geography(self):
#         try:
#             self.course.enrollment(demographic.LOCATION)
#             return True
#         except ClientError:
#             return False
#
#     def has_engagement_activity(self):
#         try:
#             self.course.activity()
#             return True
#         except ClientError:
#             return False
#
#     def has_problem_submissions(self):
#         try:
#             self.course.problems()
#             return True
#         except ClientError:
#             return False
#
#     def report(self):
#         report = {
#             'course_id': self.course_id
#         }
#
#         # Check that the pages load
#         for page in self.course_pages:
#             report[page] = self._http_status(self._build_course_url(page))
#
#         # Check API for data
#         report['api_enrollment_activity'] = self.has_enrollment_activity()
#         report['api_enrollment_geography'] = self.has_enrollment_geography()
#         report['api_activity'] = self.has_engagement_activity()
#         report['api_problems'] = self.has_problem_submissions()
#
#         return report


class CoursePerformanceReportGenerator(ReportGeneratorBase):
    """
    Generates a report on the course performance pages and data.
    """
    REPORT_NAME = 'course_performance'

    def _problems(self):
        problems = {}

        try:
            problem_list = self.analytics_api_client.courses(self.course_id).problems()
            for problem in problem_list:
                problems[problem['module_id']] = problem
        except Exception as e:  # pylint: disable=broad-except
            logger.error('Failed to retrieve problems for %s: %s\n%s', self.course_id, e, traceback.format_exc())

        return problems

    def _grading_policy(self):
        return self.course_api_client.grading_policies(self.course_id).get()

    def _assignment_types(self):
        gp = self._grading_policy()
        return [item['assignment_type'] for item in gp]

    def _structure(self):
        return self.course_api_client.course_structures(self.course_id).get()

    def _assignments(self, assignment_type=None):
        structure = self._structure()
        return CourseStructure.course_structure_to_assignments(structure, graded=True, assignment_type=assignment_type)

    def _start_date(self):
        info = self.course_api_client.courses(self.course_id).get()
        return datetime.datetime.strptime(info['start'], self.course_api_client.DATETIME_FORMAT)

    def generate_report(self):
        """
        {
            'course_id': 'edX/DemoX/Demo_Course',
            'start': '2015-01-01 00:00:00Z',
            'course_valid': true,
            'assignment_types': {
                'expected': ['Homework', 'Exam'],
                'actual': ['Homework', 'Exam'],
                'valid': true,
                'results': [
                    {
                        'name': 'Homework',
                        'expected': 3,
                        'actual': 3,
                        'valid': true,
                        'problems': {
                            'number_in_structure': 2,
                            'valid': true,
                            'number_with_submissions': 1,
                            'total_submissions': 1
                        }
                    }
                ]
            }
        }
        """
        start = self._start_date()
        report = {'course_id': self.course_id, 'start': start.strftime(self.course_api_client.DATETIME_FORMAT)}

        if start > datetime.datetime.today():
            logger.info('Course %s has not yet started.', self.course_id)

        assignment_types = sorted(self._assignment_types())
        assignments = self._assignments()
        actual_assignment_types = sorted(set([assignment['assignment_type'] for assignment in assignments]))

        expected = len(assignment_types)
        actual = len(actual_assignment_types)
        course_valid = expected == 0 or (expected == actual and (None not in actual_assignment_types))
        report['assignment_types'] = {
            'expected': assignment_types,
            'actual': actual_assignment_types,
            'valid': course_valid,
            'results': []
        }

        submissions = self._problems()
        has_submissions = len(submissions) > 0
        report['has_submissions'] = has_submissions

        if course_valid:
            for item in self._grading_policy():
                assignment_type = item['assignment_type']
                expected = item['count']
                assignments = self._assignments(assignment_type)
                actual = len(assignments)
                path = 'performance/graded_content/{}'.format(slugify(assignment_type))
                path = self.build_course_path(path)
                status, elapsed = self.get_http_status_and_load_time(self.get_dashboard_url(path))
                valid = (has_submissions and status == 200) or not has_submissions
                course_valid &= valid

                data = {
                    'name': assignment_type,
                    'status': status,
                    'load_time': elapsed,
                    'expected': expected,
                    'actual': actual,
                    'valid': valid
                }

                # Problems
                problems = []
                for assignment in assignments:
                    problems += assignment['problems']

                number_in_structure = len(problems)
                problems_with_submissions = []
                _problem_ids = []  # Do not allow duplicates
                for problem in problems:
                    problem_id = problem['id']
                    submission = submissions.get(problem_id)
                    if submission and problem_id not in problems_with_submissions:
                        problems_with_submissions.append(submission)
                        _problem_ids.append(problem_id)

                number_with_submissions = len(problems_with_submissions)
                total_submissions = sum([problem['total_submissions'] for problem in problems_with_submissions])
                problems_valid = number_in_structure > 0
                # course_valid &= problems_valid

                data['problems'] = {
                    'number_in_structure': number_in_structure,
                    'valid': problems_valid,
                    'number_with_submissions': number_with_submissions,
                    'total_submissions': total_submissions
                }

                report['assignment_types']['results'].append(data)

        report['course_valid'] = course_valid
        return course_valid, report


class CoursePerformanceScreenshotReporter(CoursePerformanceReportGenerator):
    REPORT_NAME = 'course_performance_screenshot'

    def __init__(self, course_id, http_cookies=None):
        super(CoursePerformanceScreenshotReporter, self).__init__(course_id, http_cookies)
        self.driver = webdriver.Firefox()

    def _take_screenshot(self, url_path):
        logger.debug('Screenshotting %s...', url_path)

        # Go fullscreen
        self.driver.maximize_window()

        self.driver.get(self.get_dashboard_url(url_path))
        filename = join('screenshots', '{}-{}.png'.format(slugify(self.course_id), slugify(url_path)))

        if self.driver.get_screenshot_as_file(filename):
            logger.debug('screenshot saved to %s.', filename)
            return filename

        logger.error('Failed to take screenshot of %s!', url_path)
        return None

    def _login(self):
        if ENABLE_AUTO_AUTH:
            self.driver.get(self.get_dashboard_url('/test/auto_auth/'))
        else:
            url = LMS_URL
            if BASIC_AUTH_CREDENTIALS:
                username = BASIC_AUTH_CREDENTIALS[0]
                password = BASIC_AUTH_CREDENTIALS[1]
                url = url.replace('://', '://{}:{}@'.format(username, password))

            self.driver.get('{}/login'.format(url))
            self.driver.find_element_by_id('login-email').send_keys(LMS_USERNAME)
            self.driver.find_element_by_id('login-password').send_keys(LMS_PASSWORD)
            self.driver.find_element_by_css_selector('button.login-button').click()

    def generate_report(self):
        report = {
            'course_id': self.course_id,
            'reviewed': False,
            'approved': False,
        }

        try:
            self._login()
            report['start'] = self._start_date().strftime(self.course_api_client.DATETIME_FORMAT)

            url_paths = ['performance/graded_content']
            for assignment_type in self._assignment_types():
                url_paths.append('performance/graded_content/{}'.format(slugify(assignment_type)))

            pages = []
            for url_path in url_paths:
                url_path = self.build_course_path(url_path)
                pages.append({
                    'url_path': url_path,
                    'filename': self._take_screenshot(url_path)
                })
            report['pages'] = pages
        finally:
            self.driver.close()

        return True, report


class CourseHasStructureDataReportGenerator(ReportGeneratorBase):
    """
    Verifies that the course structure API returns data for the course.
    """
    REPORT_NAME = 'course_has_structure_data'

    def generate_report(self):
        report = {'course_id': self.course_id}
        try:
            self.course_api_client.course_structures(self.course_id).get()
            valid = True
        except Exception as ex:  # pylint: disable=broad-except
            valid = False
            report['error'] = ex.message

        report['has_structure_data'] = valid
        return valid, report
