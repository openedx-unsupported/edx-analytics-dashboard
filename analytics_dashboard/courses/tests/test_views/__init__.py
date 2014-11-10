from ddt import ddt, data
import mock

from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from analyticsclient.exceptions import NotFoundError
from waffle import Switch

from analytics_dashboard.tests.test_views import RedirectTestCaseMixin, UserTestCaseMixin
from courses.permissions import set_user_course_permissions, revoke_user_course_permissions
from courses.tests.utils import set_empty_permissions, get_mock_api_enrollment_data


DEMO_COURSE_ID = 'course-v1:edX+DemoX+Demo_2014'
DEPRECATED_DEMO_COURSE_ID = 'edX/DemoX/Demo_Course'


class PermissionsTestMixin(object):
    def tearDown(self):
        super(PermissionsTestMixin, self).tearDown()
        cache.clear()

    def grant_permission(self, user, *courses):
        set_user_course_permissions(user, courses)

    def revoke_permissions(self, user):
        revoke_user_course_permissions(user)


class MockApiTestMixin(object):
    api_method = None

    def get_mock_data(self, course_id):
        raise NotImplementedError


# pylint: disable=not-callable,abstract-method
@ddt
class AuthTestMixin(MockApiTestMixin, PermissionsTestMixin, RedirectTestCaseMixin, UserTestCaseMixin):
    def setUp(self):
        super(AuthTestMixin, self).setUp()
        self.grant_permission(self.user, DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
        self.login()

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_authentication(self, course_id):
        """
        Users must be logged in to view the page.
        """

        if self.api_method:
            with mock.patch(self.api_method, return_value=self.get_mock_data(course_id)):
                # Authenticated users should go to the course page
                self.login()
                response = self.client.get(self.path(course_id), follow=True)
                self.assertEqual(response.status_code, 200)

                # Unauthenticated users should be redirected to the login page
                self.client.logout()
                response = self.client.get(self.path(course_id))
                self.assertRedirectsNoFollow(response, settings.LOGIN_URL, next=self.path(course_id))

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    @mock.patch('courses.permissions.refresh_user_course_permissions', mock.Mock(side_effect=set_empty_permissions))
    def test_authorization(self, course_id):
        """
        Users must be authorized to view a course in order to view the course pages.
        """

        if self.api_method:
            with mock.patch(self.api_method, return_value=self.get_mock_data(course_id)):
                # Authorized users should be able to view the page
                self.grant_permission(self.user, course_id)
                response = self.client.get(self.path(course_id), follow=True)
                self.assertEqual(response.status_code, 200)

                # Unauthorized users should be redirected to the 403 page
                self.revoke_permissions(self.user)
                response = self.client.get(self.path(course_id), follow=True)
                self.assertEqual(response.status_code, 403)


# pylint: disable=abstract-method
class ViewTestMixin(AuthTestMixin):
    viewname = None

    def path(self, course_id=None):
        kwargs = {}
        if course_id:
            kwargs['course_id'] = course_id

        return reverse(self.viewname, kwargs=kwargs)


@ddt
class CourseViewTestMixin(ViewTestMixin):
    presenter_method = None

    def assertPrimaryNav(self, nav, course_id):
        raise NotImplementedError

    def assertSecondaryNavs(self, nav, course_id):
        raise NotImplementedError

    def assertNavs(self, actual_navs, expected_navs, active_nav_label):
        for item in expected_navs:
            if item['label'] == active_nav_label:
                item['active'] = True
                item['href'] = '#'
            else:
                item['active'] = False

        self.assertListEqual(actual_navs, expected_navs)

    @mock.patch('courses.views.CourseValidMixin.is_valid_course', mock.Mock(return_value=False))
    def test_invalid_course(self):
        course_id = 'fakeOrg/soFake/Fake_Course'
        self.grant_permission(self.user, course_id)
        path = reverse(self.viewname, kwargs={'course_id': course_id})

        response = self.client.get(path, follow=True)
        self.assertEqual(response.status_code, 404)

    def assertViewIsValid(self, course_id):
        raise NotImplementedError

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_valid_course(self, course_id):
        self.assertViewIsValid(course_id)

    def assertValidMissingDataContext(self, context):
        raise NotImplementedError

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_missing_data(self, course_id):
        with mock.patch(self.presenter_method, mock.Mock(side_effect=NotFoundError)):
            response = self.client.get(self.path(course_id))
            context = response.context

        self.assertValidMissingDataContext(context)


# pylint: disable=abstract-method
class CourseEnrollmentViewTestMixin(CourseViewTestMixin):
    active_secondary_nav_label = None
    api_method = 'analyticsclient.course.Course.enrollment'

    def assertPrimaryNav(self, nav, course_id):
        expected = {
            'icon': 'fa-child',
            'href': reverse('courses:enrollment_activity', kwargs={'course_id': course_id}),
            'label': _('Enrollment'),
            'name': 'enrollment'
        }
        self.assertDictEqual(nav, expected)

    def assertSecondaryNavs(self, nav, course_id):
        reverse_kwargs = {'course_id': course_id}
        expected = [
            {'name': 'activity', 'label': _('Activity'),
             'href': reverse('courses:enrollment_activity', kwargs=reverse_kwargs)},
            {'name': 'demographics', 'label': _('Demographics'),
             'href': reverse('courses:enrollment_demographics_age', kwargs=reverse_kwargs)},
            {'name': 'geography', 'label': _('Geography'),
             'href': reverse('courses:enrollment_geography', kwargs=reverse_kwargs)}
        ]

        self.assertNavs(nav, expected, self.active_secondary_nav_label)

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_data(course_id)


class CourseEnrollmentDemographicsMixin(CourseEnrollmentViewTestMixin):
    active_secondary_nav_label = 'Demographics'
    active_tertiary_nav_label = None

    def format_tip_percent(self, percent):
        if percent is None:
            formatted_percent = '0'
        else:
            formatted_percent = round(percent, 3) * 100
        return formatted_percent

    def assertAllNavs(self, context, course_id):
        self.assertPrimaryNav(context['primary_nav_item'], course_id)
        self.assertSecondaryNavs(context['secondary_nav_items'], course_id)
        self.assertTertiaryNavs(context['tertiary_nav_items'], course_id)

    def assertTertiaryNavs(self, nav, course_id):
        reverse_kwargs = {'course_id': course_id}
        expected = [
            {'name': 'age', 'label': _('Age'),
             'href': reverse('courses:enrollment_demographics_age', kwargs=reverse_kwargs)},
            {'name': 'education', 'label': _('Education'),
             'href': reverse('courses:enrollment_demographics_education', kwargs=reverse_kwargs)},
            {'name': 'gender', 'label': _('Gender'),
             'href': reverse('courses:enrollment_demographics_gender', kwargs=reverse_kwargs)}
        ]
        self.assertNavs(nav, expected, self.active_tertiary_nav_label)
