from ddt import ddt
import httpretty
import mock
from mock import patch, Mock

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from waffle.testutils import override_switch

import analyticsclient.constants.activity_type as AT

from courses.tests.factories import CourseEngagementDataFactory
from courses.tests.test_views import (
    CourseViewTestMixin,
    PatchMixin,
    CourseStructureViewMixin,
    CourseAPIMixin)
from courses.tests import utils
from courses.tests.utils import CourseSamples


@override_switch('enable_engagement_videos_pages', active=True)
class CourseEngagementViewTestMixin(PatchMixin, CourseAPIMixin):  # pylint: disable=abstract-method
    api_method = 'analyticsclient.course.Course.activity'
    active_secondary_nav_label = None

    def setUp(self):
        super(CourseEngagementViewTestMixin, self).setUp()
        # This view combines the activity API with the enrollment API, so we need to mock both.
        patcher = mock.patch('analyticsclient.course.Course.enrollment', return_value=utils.mock_course_enrollment())
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_mock_data(self, course_id):
        return utils.mock_course_activity(course_id)

    def assertPrimaryNav(self, nav, course_id):
        expected = {
            'icon': 'fa-bar-chart',
            'href': reverse('courses:engagement:content', kwargs={'course_id': course_id}),
            'text': 'Engagement',
            'translated_text': _('Engagement'),
            'name': 'engagement',
            'fragment': '',
            'scope': 'course',
            'lens': 'engagement',
            'report': 'content',
            'depth': ''
        }
        self.assertDictEqual(nav, expected)

    def get_expected_secondary_nav(self, _course_id):
        # override for each secondary page
        return [
            {
                'active': True,
                'href': '#',
                'name': 'content',
                'text': 'Content',
                'translated_text': _('Content'),
                'scope': 'course',
                'lens': 'engagement',
                'report': 'content',
                'depth': ''
            },
            {
                'active': True,
                'href': '#',
                'name': 'videos',
                'text': 'Videos',
                'translated_text': _('Videos'),
                'scope': 'course',
                'lens': 'engagement',
                'report': 'videos',
                'depth': ''
            },
        ]

    def assertSecondaryNavs(self, nav, course_id):
        expected = self.get_expected_secondary_nav(course_id)
        self.assertListEqual(nav, expected)


@override_switch('enable_engagement_videos_pages', active=True)
@ddt
class CourseEngagementContentViewTests(CourseViewTestMixin, CourseEngagementViewTestMixin, TestCase):
    viewname = 'courses:engagement:content'
    presenter_method = 'courses.presenters.engagement.CourseEngagementActivityPresenter.get_summary_and_trend_data'
    active_secondary_nav_label = 'Content'

    def get_expected_secondary_nav(self, course_id):
        expected = super(CourseEngagementContentViewTests, self).get_expected_secondary_nav(course_id)
        expected[1].update({
            'href': reverse('courses:engagement:videos', kwargs={'course_id': course_id}),
            'active': False
        })
        return expected

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


@override_switch('enable_engagement_videos_pages', active=True)
@ddt
class CourseEngagementVideoMixin(CourseEngagementViewTestMixin, CourseStructureViewMixin):
    active_secondary_nav_label = 'Video'
    sections = None

    def get_expected_secondary_nav(self, course_id):
        expected = super(CourseEngagementVideoMixin, self).get_expected_secondary_nav(course_id)
        expected[0].update({
            'href': reverse('courses:engagement:content', kwargs={'course_id': course_id}),
            'active': False
        })
        return expected

    @httpretty.activate
    def test_invalid_course(self):
        self._test_invalid_course(self.COURSE_BLOCKS_API_TEMPLATE)

    def setUp(self):
        super(CourseEngagementVideoMixin, self).setUp()
        self.factory = CourseEngagementDataFactory()
        self.sections = self.factory.presented_sections
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.sections',
                    return_value=self.sections)
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.section',
                    return_value=self.sections[0])
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.subsections',
                    return_value=self.sections[0]['children'])
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.subsection',
                    return_value=self.sections[0]['children'][0])
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.subsection_children',
                    return_value=self.sections[0]['children'][0]['children'])
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.get_video_timeline',
                    return_value=self.factory.get_presented_video_timeline())
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.block',
                    return_value=self.sections[0]['children'][0]['children'][0])
        self._patch('courses.presenters.engagement.CourseEngagementVideoPresenter.subsection_child',
                    return_value=self.sections[0]['children'][0]['children'][0])
        self.start_patching()

    def assertValidContext(self, context):
        expected = {
            'sections': self.sections,
        }
        self.assertDictContainsSubset(expected, context)

    @httpretty.activate
    @patch('courses.presenters.engagement.CourseEngagementVideoPresenter.sections', Mock(return_value=dict()))
    def test_missing_sections(self):
        """ Every video page will use sections and will return 200 if sections aren't available. """
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID)
        response = self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID))
        # base page will should return a 200 even if no sections found
        self.assertEqual(response.status_code, 200)


class EngagementVideoCourseTest(CourseEngagementVideoMixin, TestCase):
    viewname = 'courses:engagement:videos'


class EngagementVideoCourseSectionTest(CourseEngagementVideoMixin, TestCase):
    viewname = 'courses:engagement:video_section'

    def path(self, **kwargs):
        # Use default kwargs for tests that don't necessarily care about the specific argument values.
        default_kwargs = {
            'section_id': self.sections[0]['id'],
        }
        default_kwargs.update(kwargs)
        kwargs = default_kwargs

        return super(EngagementVideoCourseSectionTest, self).path(**kwargs)

    def assertValidContext(self, context):
        super(EngagementVideoCourseSectionTest, self).assertValidContext(context)
        self.assertEqual(self.sections[0], context['section'])
        self.assertListEqual(self.sections[0]['children'], context['subsections'])

    @httpretty.activate
    @patch('courses.presenters.engagement.CourseEngagementVideoPresenter.section', Mock(return_value=None))
    def test_missing_section(self):
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID)
        response = self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID, section_id='Invalid'))
        self.assertEqual(response.status_code, 404)


class EngagementVideoCourseSubsectionTest(CourseEngagementVideoMixin, TestCase):
    viewname = 'courses:engagement:video_subsection'

    def path(self, **kwargs):
        # Use default kwargs for tests that don't necessarily care about the specific argument values.
        default_kwargs = {
            'section_id': self.sections[0]['id'],
            'subsection_id': self.sections[0]['children'][0]['id'],
        }
        default_kwargs.update(kwargs)
        kwargs = default_kwargs

        return super(EngagementVideoCourseSubsectionTest, self).path(**kwargs)

    def assertValidContext(self, context):
        super(EngagementVideoCourseSubsectionTest, self).assertValidContext(context)
        section = self.sections[0]
        self.assertEqual(section, context['section'])
        self.assertListEqual(section['children'], context['subsections'])
        self.assertEqual(section['children'][0], context['subsection'])

    @httpretty.activate
    @patch('courses.presenters.engagement.CourseEngagementVideoPresenter.subsection', Mock(return_value=None))
    def test_missing_subsection(self):
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID)
        response = self.client.get(self.path(
            course_id=CourseSamples.DEMO_COURSE_ID, section_id='Invalid', subsection_id='Nope'))
        self.assertEqual(response.status_code, 404)


class EngagementVideoCourseTimelineTest(CourseEngagementVideoMixin, TestCase):
    viewname = 'courses:engagement:video_timeline'

    def path(self, **kwargs):
        # Use default kwargs for tests that don't necessarily care about the specific argument values.
        default_kwargs = {
            'section_id': self.sections[0]['id'],
            'subsection_id': self.sections[0]['children'][0]['id'],
            'video_id': self.sections[0]['children'][0]['children'][0]['id']
        }
        default_kwargs.update(kwargs)
        kwargs = default_kwargs
        return super(EngagementVideoCourseTimelineTest, self).path(**kwargs)

    def assertValidContext(self, context):
        super(EngagementVideoCourseTimelineTest, self).assertValidContext(context)
        section = self.sections[0]
        self.assertEqual(section, context['section'])
        self.assertListEqual(section['children'], context['subsections'])
        self.assertEqual(section['children'][0], context['subsection'])
        self.assertEqual(section['children'][0]['children'], context['subsection_children'])
        self.assertEqual(section['children'][0]['children'][0], context['summary_metrics'])
        self.assertListEqual(self.factory.get_presented_video_timeline(),
                             context['js_data']['course']['videoTimeline'])

    @httpretty.activate
    @patch('courses.presenters.engagement.CourseEngagementVideoPresenter.subsection_child', Mock(return_value=None))
    def test_missing_video_module(self):
        """ Every video page will use sections and will return 200 if sections aren't available. """
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID)
        response = self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID))
        # base page will should return a 200 even if no sections found
        self.assertEqual(response.status_code, 404)

    @httpretty.activate
    @patch('courses.presenters.engagement.CourseEngagementVideoPresenter.get_video_timeline', Mock(return_value=None))
    def test_missing_video_data(self):
        self.mock_course_detail(CourseSamples.DEMO_COURSE_ID)
        response = self.client.get(self.path(course_id=CourseSamples.DEMO_COURSE_ID))
        # page will still be displayed, but with error messages
        self.assertEqual(response.status_code, 200)
