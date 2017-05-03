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
        presenter_method = 'courses.presenters.course_summaries.CourseSummariesPresenter.get_course_summaries'
        programs_presenter_method = 'courses.presenters.programs.ProgramsPresenter.get_programs'
        mock_data = self.get_mock_data(course_ids)
        programs_mock_data = self.get_programs_mock_data(course_ids)

        with mock.patch(permissions_method, return_value=course_ids):
            with mock.patch(presenter_method, return_value=mock_data) as summaries_presenter:
                with mock.patch(programs_presenter_method, return_value=programs_mock_data) as programs_presenter:
                    response = self.client.get(self.path())
                    self.assertEqual(response.status_code, 200)
                    context = response.context
                    page_data = json.loads(context['page_data'])
                    self.assertListEqual(page_data['course']['course_list_json'], self.expected_summaries(course_ids))
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
