# pylint: disable=abstract-method

from ddt import data, ddt
import httpretty
import mock
from waffle.testutils import override_switch

from django.test import TestCase

from analyticsclient.exceptions import NotFoundError

from courses.tests.test_views import CourseViewTestMixin
from courses.tests.utils import CourseSamples


@ddt
class CourseHomeViewTests(CourseViewTestMixin, TestCase):
    viewname = 'courses:home'

    def assertViewIsValid(self, course_id):
        response = self.client.get(self.path(course_id=course_id))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['page_title'], 'Course Home')
        self.assertValidCourseName(course_id, response.context)

    def assert_performance_report_link_present(self, expected):
        """
        Assert that the Problem Response Report download link is or is not present.
        """
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID, {})
        path = self.path(course_id=CourseSamples.DEMO_COURSE_ID)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_title'], 'Course Home')
        performance_item = next(g for g in response.context['table_items'] if unicode(g['name']) == u'Performance')
        performance_views = [item['view'] for item in performance_item['items']]
        self.assertEqual('courses:csv:performance_problem_responses' in performance_views, expected)

    @data(CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID)
    def test_missing_data(self, course_id):
        self.skipTest('The course homepage does not check for the existence of a course.')

    @httpretty.activate
    @override_switch('enable_course_api', active=True)
    def test_course_overview(self):
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID, {'start': '2015-01-23T00:00:00Z', 'end': None})
        response = self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID))
        self.assertEqual(response.status_code, 200)

        overview_data = {k: v for k, v in response.context['course_overview']}
        self.assertEqual(overview_data.get('Start Date'), 'January 23, 2015')
        self.assertEqual(overview_data.get('Status'), 'In Progress')
        links = {link['title']: link['url'] for link in response.context['external_course_tools']}
        self.assertEqual(len(links), 3)
        self.assertEqual(links.get('Instructor Dashboard'),
                         'http://lms-host/{}/instructor'.format(CourseSamples.DEMO_COURSE_ID))
        self.assertEqual(links.get('Courseware'), 'http://lms-host/{}/courseware'.format(CourseSamples.DEMO_COURSE_ID))
        self.assertEqual(links.get('Studio'), 'http://cms-host/{}'.format(CourseSamples.DEMO_COURSE_ID))

    @httpretty.activate
    @override_switch('enable_course_api', active=True)
    def test_course_ended(self):
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID, {
            'start': '2015-01-01T00:00:00Z',
            'end': '2015-02-15T00:00:00Z'
        })
        response = self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID))
        self.assertEqual(response.status_code, 200)
        overview_data = {k: v for k, v in response.context['course_overview']}
        self.assertEqual(overview_data.get('Start Date'), 'January 01, 2015')
        self.assertEqual(overview_data.get('End Date'), 'February 15, 2015')
        self.assertEqual(overview_data.get('Status'), 'Ended')

    @httpretty.activate
    @override_switch('enable_course_api', active=True)
    def test_performance_problem_response_link_default(self):
        """
        Ensure the problem response link is disabled by default
        """
        self.assert_performance_report_link_present(False)

    @data(True, False)
    @httpretty.activate
    @override_switch('enable_course_api', active=True)
    @override_switch('enable_problem_response_download', active=True)
    @mock.patch('courses.presenters.performance.CourseReportDownloadPresenter.get_report_info')
    def test_performance_problem_response_link_enabled(self, available, mock_get_report_info):
        """
        When enabled, ensure the problem response link is shown only if a report is available
        """
        if available:
            mock_get_report_info.return_value = {'download_url': 'https://some/url.csv'}
        else:
            mock_get_report_info.side_effect = NotFoundError
        self.assert_performance_report_link_present(available)
