from ddt import ddt
import mock
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import analyticsclient.constants.activity_type as AT

from courses.tests.test_views import CourseViewTestMixin
from courses.tests import utils


class CourseEngagementViewTestMixin(CourseViewTestMixin):  # pylint: disable=abstract-method
    api_method = 'analyticsclient.course.Course.activity'

    def get_mock_data(self, course_id):
        return utils.mock_course_activity(course_id)

    def assertPrimaryNav(self, nav, course_id):
        expected = {
            'icon': 'fa-bar-chart',
            'href': reverse('courses:engagement:content', kwargs={'course_id': course_id}),
            'label': _('Engagement'),
            'name': 'engagement'
        }
        self.assertDictEqual(nav, expected)

    def assertSecondaryNavs(self, nav, course_id):
        expected = [{'active': True, 'name': 'content', 'label': _('Content'), 'href': '#'}]
        self.assertListEqual(nav, expected)


@ddt
class CourseEngagementContentViewTests(CourseEngagementViewTestMixin, TestCase):
    viewname = 'courses:engagement:content'
    presenter_method = 'courses.presenters.engagement.CourseEngagementPresenter.get_summary_and_trend_data'

    def assertViewIsValid(self, course_id):
        rv = utils.mock_engagement_activity_summary_and_trend_data()
        with mock.patch(self.presenter_method, mock.Mock(return_value=rv)):
            response = self.client.get(self.path(course_id=course_id))

            # make sure that we get a 200
            self.assertEqual(response.status_code, 200)

            # check page title
            self.assertEqual(response.context['page_title'], 'Engagement Content')

            # make sure the summary numbers are correct
            self.assertEqual(response.context['summary'][AT.ANY], 100)
            self.assertEqual(response.context['summary'][AT.ATTEMPTED_PROBLEM], 301)
            self.assertEqual(response.context['summary'][AT.PLAYED_VIDEO], 1000)
            self.assertEqual(response.context['summary'][AT.POSTED_FORUM], 0)

            # check to make sure the activity trends are correct
            trends = response.context['js_data']['course']['engagementTrends']
            self.assertEqual(len(trends), 2)
            expected = {
                'weekEnding': '2013-01-08',
                AT.ANY: 100,
                AT.ATTEMPTED_PROBLEM: 301,
                AT.PLAYED_VIDEO: 1000,
                AT.POSTED_FORUM: 0
            }
            self.assertDictEqual(trends[0], expected)

            expected = {
                'weekEnding': '2013-01-01',
                AT.ANY: 1000,
                AT.ATTEMPTED_PROBLEM: 0,
                AT.PLAYED_VIDEO: 10000,
                AT.POSTED_FORUM: 45
            }
            self.assertDictEqual(trends[1], expected)

            self.assertPrimaryNav(response.context['primary_nav_item'], course_id)
            self.assertSecondaryNavs(response.context['secondary_nav_items'], course_id)

            self.assertValidCourseName(course_id, response.context)

    def assertValidMissingDataContext(self, context):
        # summary and engagementTrends should evaluate to falsy values, which the
        # template evaluates to render error messages
        self.assertIsNone(context['summary'])
        self.assertIsNone(context['js_data']['course']['engagementTrends'])
