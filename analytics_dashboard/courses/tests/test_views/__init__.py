import json
import logging

from analyticsclient.exceptions import NotFoundError
from ddt import ddt, data
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import ugettext_lazy as _
import httpretty
import mock
from mock import patch, Mock, _is_started

from core.tests.test_views import RedirectTestCaseMixin, UserTestCaseMixin
from courses.permissions import set_user_course_permissions, revoke_user_course_permissions
from courses.tests import SwitchMixin
from courses.tests.utils import set_empty_permissions, get_mock_api_enrollment_data, mock_course_name


DEMO_COURSE_ID = 'course-v1:edX+DemoX+Demo_2014'
DEPRECATED_DEMO_COURSE_ID = 'edX/DemoX/Demo_Course'

logger = logging.getLogger(__name__)


class CourseAPIMixin(SwitchMixin):
    """
    Mixin with methods to help mock the course API.
    """

    COURSE_API_COURSE_LIST = {'next': None, 'results': [
        {'id': course_key, 'name': 'Test ' + course_key} for course_key in [DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID]
    ]}

    def mock_course_api(self, path, body=None, **kwargs):
        """
        Registers an HTTP mock for the specified course API path. The mock returns the specified data.

        The calling test function MUST activate httpretty.

        Arguments
            body    --  Data returned by the mocked API
            kwargs  --  Additional arguments passed to httpretty.register_uri()
        """

        # Avoid developer confusion when httpretty is not active and fail the test now.
        if not httpretty.is_enabled():
            self.fail('httpretty is not enabled. The mock will not be used!')

        body = body or {}

        # Remove trailing slashes from the path. They will be added back later.
        path = path.strip(u'/')
        url = '{}/{}/'.format(settings.COURSE_API_URL, path)

        default_kwargs = {
            'body': kwargs.get('body', json.dumps(body)),
            'content_type': 'application/json'
        }
        default_kwargs.update(kwargs)

        httpretty.register_uri(httpretty.GET, url, **default_kwargs)
        logger.debug('Mocking Course API URL: %s', url)

    def mock_course_detail(self, course_id, extra=None):
        path = 'courses/{}'.format(course_id)
        body = {'id': course_id, 'name': mock_course_name(course_id)}
        if extra:
            body.update(extra)
        self.mock_course_api(path, body)

    def mock_course_list(self):
        self.mock_course_api('courses', self.COURSE_API_COURSE_LIST)


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
                response = self.client.get(self.path(course_id=course_id), follow=True)
                self.assertEqual(response.status_code, 200)

                # Unauthenticated users should be redirected to the login page
                self.client.logout()
                response = self.client.get(self.path(course_id=course_id))
                self.assertRedirectsNoFollow(response, settings.LOGIN_URL, next=self.path(course_id=course_id))

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
                response = self.client.get(self.path(course_id=course_id), follow=True)
                self.assertEqual(response.status_code, 200)

                # Unauthorized users should be redirected to the 403 page
                self.revoke_permissions(self.user)
                response = self.client.get(self.path(course_id=course_id), follow=True)
                self.assertEqual(response.status_code, 403)


# pylint: disable=abstract-method
class ViewTestMixin(AuthTestMixin):
    viewname = None
    presenter_method = None

    def path(self, **kwargs):
        return reverse(self.viewname, kwargs=kwargs)


class NavAssertMixin(object):
    def generate_course_name(self, course_id):
        return 'Test ' + course_id

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


@ddt
class CourseViewTestMixin(CourseAPIMixin, NavAssertMixin, ViewTestMixin):
    @mock.patch('courses.views.CourseValidMixin.is_valid_course', mock.Mock(return_value=False))
    def test_invalid_course(self):
        course_id = 'fakeOrg/soFake/Fake_Course'
        self.grant_permission(self.user, course_id)
        path = reverse(self.viewname, kwargs={'course_id': course_id})

        response = self.client.get(path, follow=True)
        self.assertEqual(response.status_code, 404)

    def assertViewIsValid(self, course_id):
        raise NotImplementedError

    @httpretty.activate
    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_valid_course(self, course_id):
        self.toggle_switch('enable_course_api', True)
        self.toggle_switch('display_course_name_in_nav', True)
        self.mock_course_detail(course_id)
        self.assertViewIsValid(course_id)

    def assertValidMissingDataContext(self, context):
        raise NotImplementedError

    @data(DEMO_COURSE_ID, DEPRECATED_DEMO_COURSE_ID)
    def test_missing_data(self, course_id):
        with mock.patch(self.presenter_method, mock.Mock(side_effect=NotFoundError)):
            response = self.client.get(self.path(course_id=course_id))
            context = response.context

        self.assertValidMissingDataContext(context)

    def assertValidCourseName(self, course_id, context):
        course_name = self.generate_course_name(course_id)
        self.assertEqual(context['course_name'], course_name)


# pylint: disable=abstract-method
class CourseEnrollmentViewTestMixin(CourseViewTestMixin):
    active_secondary_nav_label = None
    api_method = 'analyticsclient.course.Course.enrollment'

    def assertPrimaryNav(self, nav, course_id):
        expected = {
            'icon': 'fa-child',
            'href': reverse('courses:enrollment:activity', kwargs={'course_id': course_id}),
            'label': _('Enrollment'),
            'name': 'enrollment'
        }
        self.assertDictEqual(nav, expected)

    def assertSecondaryNavs(self, nav, course_id):
        reverse_kwargs = {'course_id': course_id}
        expected = [
            {'name': 'activity', 'label': _('Activity'),
             'href': reverse('courses:enrollment:activity', kwargs=reverse_kwargs)},
            {'name': 'demographics', 'label': _('Demographics'),
             'href': reverse('courses:enrollment:demographics_age', kwargs=reverse_kwargs)},
            {'name': 'geography', 'label': _('Geography'),
             'href': reverse('courses:enrollment:geography', kwargs=reverse_kwargs)}
        ]

        self.assertNavs(nav, expected, self.active_secondary_nav_label)

    def get_mock_data(self, course_id):
        return get_mock_api_enrollment_data(course_id)


class CourseEnrollmentDemographicsMixin(CourseEnrollmentViewTestMixin):
    active_secondary_nav_label = 'Demographics'
    active_tertiary_nav_label = None

    def format_tip_percent(self, value):
        if value is None:
            formatted_percent = u'0'
        else:
            formatted_percent = intcomma(round(value, 3) * 100)

        return formatted_percent

    def assertAllNavs(self, context, course_id):
        self.assertPrimaryNav(context['primary_nav_item'], course_id)
        self.assertSecondaryNavs(context['secondary_nav_items'], course_id)
        self.assertTertiaryNavs(context['tertiary_nav_items'], course_id)

    def assertTertiaryNavs(self, nav, course_id):
        reverse_kwargs = {'course_id': course_id}
        expected = [
            {'name': 'age', 'label': _('Age'),
             'href': reverse('courses:enrollment:demographics_age', kwargs=reverse_kwargs)},
            {'name': 'education', 'label': _('Education'),
             'href': reverse('courses:enrollment:demographics_education', kwargs=reverse_kwargs)},
            {'name': 'gender', 'label': _('Gender'),
             'href': reverse('courses:enrollment:demographics_gender', kwargs=reverse_kwargs)}
        ]
        self.assertNavs(nav, expected, self.active_tertiary_nav_label)


class PatchMixin(object):
    patches = []

    def _patch(self, target, **mock_kwargs):
        self.patches.append(patch(target, Mock(**mock_kwargs)))

    def start_patching(self):
        for _patch in self.patches:
            _patch.start()

    def stop_patching(self):
        for _patch in self.patches:
            if _is_started(_patch):
                _patch.stop()

    def clear_patches(self):
        self.stop_patching()
        self.patches = []

    def setUp(self):
        super(PatchMixin, self).setUp()
        # Ensure patches from previous test failures are removed and de-referenced
        self.clear_patches()

    def tearDown(self):
        super(PatchMixin, self).tearDown()
        self.clear_patches()


class CourseStructureViewMixin(NavAssertMixin, ViewTestMixin):

    def assertValidContext(self, context):
        raise NotImplementedError

    @httpretty.activate
    def test_valid_course(self):
        """
        The view should return HTTP 200 if the course is valid.

        Additional assertions should be added to validate page content.
        """

        course_id = DEMO_COURSE_ID

        # Mock the course details
        self.mock_course_detail(course_id)

        # Retrieve the page. Validate the status code and context.
        response = self.client.get(self.path(course_id=course_id))
        self.assertEqual(response.status_code, 200)
        self.assertValidContext(response.context)

        self.assertPrimaryNav(response.context['primary_nav_item'], course_id)
        self.assertSecondaryNavs(response.context['secondary_nav_items'], course_id)

    def test_invalid_course(self):
        """
        The view will return HTTP 404 if the course is invalid.
        """
        raise NotImplementedError

    def _test_invalid_course(self, api_template):
        self.stop_patching()

        course_id = 'fakeOrg/soFake/Fake_Course'
        self.grant_permission(self.user, course_id)
        self.mock_course_detail(course_id)
        path = self.path(course_id=course_id)

        # The course API would return a 404 for an invalid course. Simulate it to
        # force an error in the view.
        api_path = api_template.format(course_id)
        self.mock_course_api(api_path, status=404)

        response = self.client.get(path, follow=True)
        self.assertEqual(response.status_code, 404)

    def _test_api_error(self):
        # We need to break the methods that we normally patch.
        self.stop_patching()

        course_id = DEMO_COURSE_ID
        self.mock_course_detail(course_id)

        path = self.path(course_id=course_id)
        self.assertRaises(Exception, self.client.get, path, follow=True)
