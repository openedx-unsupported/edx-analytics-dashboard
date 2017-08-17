import json

from ddt import data, ddt
import mock

from django.test import TestCase
from waffle.testutils import override_switch

from courses.tests.test_views import ViewTestMixin
from courses.exceptions import PermissionsRetrievalFailedError
from courses.tests.test_middleware import CoursePermissionsExceptionMixin
import courses.tests.utils as utils
from courses.tests.utils import CourseSamples


@ddt
class CourseSummariesViewTests(ViewTestMixin, CoursePermissionsExceptionMixin, TestCase):
    viewname = 'courses:index'

    def setUp(self):
        super(CourseSummariesViewTests, self).setUp()
        self.grant_permission(self.user, CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID)

    def get_mock_data(self, course_ids):
        return [{'course_id': course_id} for course_id in course_ids], utils.CREATED_DATETIME

    def get_programs_mock_data(self, course_ids):
        return [{'program_id': 'Demo_Program', 'course_ids': course_ids}]

    def assertCourseListEquals(self, courses):
        response = self.client.get(self.path())
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['courses'], courses)

    def expected_summaries(self, course_ids):
        return self.get_mock_data(course_ids)[0]

    def expected_programs(self, course_ids):
        return self.get_programs_mock_data(course_ids)

    def get_mock_totals(self):
        return {
            'count': 196513,
            'verified_enrollment': None,
            'cumulative_count': 251620,
            'count_change_7_days': -18
        }

    def expected_totals(self):
        """ Expected summary totals data is exactly the same as the mocked data. """
        return self.get_mock_totals()

    @override_switch('enable_course_filters', active=True)
    @data(
        [CourseSamples.DEMO_COURSE_ID],
        [CourseSamples.DEPRECATED_DEMO_COURSE_ID],
        [CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID]
    )
    def test_get(self, course_ids):
        """
        Test data is returned in the correct hierarchy.
        """
        permissions_method = 'courses.views.course_summaries.permissions.get_user_course_permissions'
        totals_summaries_method = 'courses.presenters.course_totals.CourseTotalsPresenter.get_course_totals'
        programs_method = 'courses.presenters.programs.ProgramsPresenter.get_programs'
        totals_mock_data = self.get_mock_totals()
        programs_mock_data = self.get_programs_mock_data(course_ids)

        with mock.patch(permissions_method, return_value=course_ids):
            with mock.patch(totals_summaries_method, return_value=totals_mock_data) as summaries_presenter:
                with mock.patch(programs_method, return_value=programs_mock_data) as programs_presenter:
                    response = self.client.get(self.path())
                    self.assertEqual(response.status_code, 200)
                    context = response.context
                    self.assertDictEqual(context['summary'], self.expected_totals())
                    page_data = json.loads(context['page_data'])
                    self.assertListEqual(page_data['course']['programs_json'], self.expected_programs(course_ids))
                    summaries_presenter.assert_called_with(course_ids)
                    programs_presenter.assert_called_with(course_ids=course_ids)

    def test_get_unauthorized(self):
        """ The view should raise an error if the user has no course permissions. """
        self.grant_permission(self.user)
        response = self.client.get(self.path())
        self.assertEqual(response.status_code, 403)

    @mock.patch('courses.permissions.get_user_course_permissions',
                mock.Mock(side_effect=PermissionsRetrievalFailedError))
    def test_get_with_permissions_error(self):
        response = self.client.get(self.path())
        self.assertIsPermissionsRetrievalFailedResponse(response)
