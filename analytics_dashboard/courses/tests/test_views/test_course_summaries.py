import json

from ddt import data, ddt
import mock

from django.test import TestCase

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

    def assertCourseListEquals(self, courses):
        response = self.client.get(self.path())
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.context['courses'], courses)

    def expected_summaries(self, course_ids):
        return self.get_mock_data(course_ids)[0]

    @data(
        [CourseSamples.DEMO_COURSE_ID],
        [CourseSamples.DEPRECATED_DEMO_COURSE_ID],
        [CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID]
    )
    def test_get(self, course_ids):
        """
        Test data is returned in the correct hierarchy.
        """
        presenter_method = 'courses.presenters.course_summaries.CourseSummariesPresenter.get_course_summaries'
        mock_data = self.get_mock_data(course_ids)
        with mock.patch(presenter_method, return_value=mock_data):
            response = self.client.get(self.path())
            self.assertEqual(response.status_code, 200)
            context = response.context
            page_data = json.loads(context['page_data'])
            self.assertListEqual(page_data['course']['course_list_json'], self.expected_summaries(course_ids))

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
