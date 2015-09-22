from __future__ import division
import copy
import datetime

import analyticsclient.constants.activity_type as AT
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
import mock
from ddt import ddt, data

from courses.exceptions import NoVideosError
from courses.presenters import BasePresenter
from courses.presenters.engagement import (
    CourseEngagementActivityPresenter,
    CourseEngagementTypologyPresenter,
    CourseEngagementVideoPresenter,
)
from courses.presenters.enrollment import (CourseEnrollmentPresenter, CourseEnrollmentDemographicsPresenter)
from courses.presenters.performance import CoursePerformancePresenter
from courses.tests import utils, SwitchMixin
from courses.tests.factories import CourseEngagementDataFactory, CoursePerformanceDataFactory


class BasePresenterTests(TestCase):
    def setUp(self):
        self.presenter = BasePresenter('edX/DemoX/Demo_Course')

    def test_init(self):
        presenter = BasePresenter('edX/DemoX/Demo_Course')
        self.assertEqual(presenter.client.timeout, 10)

        presenter = BasePresenter('edX/DemoX/Demo_Course', timeout=15)
        self.assertEqual(presenter.client.timeout, 15)

    def test_parse_api_date(self):
        self.assertEqual(self.presenter.parse_api_date('2014-01-01'), datetime.date(year=2014, month=1, day=1))

    def test_parse_api_datetime(self):
        self.assertEqual(self.presenter.parse_api_datetime(u'2014-09-18T145957'),
                         datetime.datetime(year=2014, month=9, day=18, hour=14, minute=59, second=57))

    def test_strip_time(self):
        self.assertEqual(self.presenter.strip_time('2014-01-01T000000'), '2014-01-01')

    def test_get_current_date(self):
        dt_format = '%Y-%m-%d'
        self.assertEqual(self.presenter.get_current_date(), datetime.datetime.utcnow().strftime(dt_format))


class CourseEngagementActivityPresenterTests(SwitchMixin, TestCase):

    def setUp(self):
        super(CourseEngagementActivityPresenterTests, self).setUp()
        self.course_id = 'this/course/id'
        self.presenter = CourseEngagementActivityPresenter(self.course_id)

    def get_expected_trends(self, include_forum_data):
        trends = [
            {
                'weekEnding': '2014-08-31',
                AT.ANY: 1000,
                AT.ATTEMPTED_PROBLEM: 0,
                AT.PLAYED_VIDEO: 10000
            }, {
                'weekEnding': '2014-09-07',
                AT.ANY: 100,
                AT.ATTEMPTED_PROBLEM: 301,
                AT.PLAYED_VIDEO: 1000,

            }
        ]

        if include_forum_data:
            trends[0][AT.POSTED_FORUM] = 45
            trends[1][AT.POSTED_FORUM] = 0

        return trends

    def get_expected_trends_small(self, include_forum_data):
        trends = self.get_expected_trends(include_forum_data)
        trends[0].update({
            AT.ANY: 0,
            AT.ATTEMPTED_PROBLEM: 0,
            AT.PLAYED_VIDEO: 0
        })

        if include_forum_data:
            trends[0][AT.POSTED_FORUM] = 0

        return trends

    def assertSummaryAndTrendsValid(self, include_forum_activity, expected_trends):
        self.toggle_switch('show_engagement_forum_activity', include_forum_activity)

        summary, trends = self.presenter.get_summary_and_trend_data()

        # Validate the trends
        self.assertEqual(len(expected_trends), len(trends))
        self.assertDictEqual(expected_trends[0], trends[0])
        self.assertDictEqual(expected_trends[1], trends[1])

        # Validate the summary
        expected_summary = utils.mock_course_activity()[1]
        del expected_summary['created']
        del expected_summary['interval_end']
        del expected_summary['course_id']

        if not include_forum_activity:
            del expected_summary[AT.POSTED_FORUM]

        expected_summary['last_updated'] = utils.CREATED_DATETIME

        self.assertDictEqual(summary, expected_summary)

    @mock.patch('analyticsclient.course.Course.activity', mock.Mock(side_effect=utils.mock_course_activity))
    def test_get_summary_and_trend_data(self):
        self.assertSummaryAndTrendsValid(False, self.get_expected_trends(False))
        self.assertSummaryAndTrendsValid(True, self.get_expected_trends(True))

    @mock.patch('analyticsclient.course.Course.activity')
    def test_get_summary_and_trend_data_small(self, mock_activity):
        api_trend = [utils.mock_course_activity()[-1]]
        mock_activity.return_value = api_trend

        self.assertSummaryAndTrendsValid(False, self.get_expected_trends_small(False))
        self.assertSummaryAndTrendsValid(True, self.get_expected_trends_small(True))


class CourseEngagementTypologyPresenterTests(TestCase):

    def setUp(self):
        super(CourseEngagementTypologyPresenterTests, self).setUp()
        self.course_id = 'course-v1:Typology+TEST+123'
        self.created_date = "2015-08-20T043618"
        access_token = 'test'
        self.presenter = CourseEngagementTypologyPresenter(access_token, self.course_id)

    def get_mock_input_data_from_api(self):
        """ Get data to mock the analytics API typology endpoint """
        return [
            {"chapter_id": "week1", "video_type": 0, "problem_type": 2, "num_users": 250, "created": self.created_date},
            {"chapter_id": "week1", "video_type": 1, "problem_type": 0, "num_users": 350, "created": self.created_date},
            {"chapter_id": "week1", "video_type": 1, "problem_type": 1, "num_users": 300, "created": self.created_date},
            {"chapter_id": "week1", "video_type": 1, "problem_type": 2, "num_users": 100, "created": self.created_date},
            {"chapter_id": "invalid", "video_type": 1, "problem_type": 2, "num_users": 3, "created": self.created_date},
        ]

    def get_mock_course_structure(self):
        """ Get data to mock the course structure """
        return {
            "root": "block-v1:Typology+TEST+123+type@course+block@course",
            "blocks": {
                "block-v1:Typology+TEST+123+type@course+block@course": {
                    "children": [
                        "block-v1:Typology+TEST+123+type@chapter+block@week1",
                        "block-v1:Typology+TEST+123+type@chapter+block@week2",
                    ]
                },
                "block-v1:Typology+TEST+123+type@chapter+block@week1": {
                    "id": "block-v1:Typology+TEST+123+type@chapter+block@week1",
                    "type": "chapter", "display_name": "Week 1: Introduction",
                },
                "block-v1:Typology+TEST+123+type@chapter+block@week2": {
                    "id": "block-v1:Typology+TEST+123+type@chapter+block@week2",
                    "type": "chapter", "display_name": "Week 2: Typologizing",
                },
            }
        }

    def get_expected_data(self):
        """ Get the data expected back from the presenter """
        return [
            {
                "id": "week1",
                "index": 1,
                "name": "Week 1: Introduction",
                "all_v_all_p": 0, "all_v_all_p_fraction": 0.0,
                "some_v_all_p": 100, "some_v_all_p_fraction": 0.10,
                "no_v_all_p": 250, "no_v_all_p_fraction": 0.25,
                "all_v_some_p": 0, "all_v_some_p_fraction": 0.0,
                "some_v_some_p": 300, "some_v_some_p_fraction": 0.30,
                "no_v_some_p": 0, "no_v_some_p_fraction": 0.0,
                "all_v_no_p": 0, "all_v_no_p_fraction": 0.0,
                "some_v_no_p": 350, "some_v_no_p_fraction": 0.35,
            },
            {
                "id": "week2",
                "index": 2,
                "name": "Week 2: Typologizing",
                "all_v_all_p": 0, "all_v_all_p_fraction": 0.0,
                "some_v_all_p": 0, "some_v_all_p_fraction": 0.0,
                "no_v_all_p": 0, "no_v_all_p_fraction": 0.0,
                "all_v_some_p": 0, "all_v_some_p_fraction": 0.0,
                "some_v_some_p": 0, "some_v_some_p_fraction": 0.0,
                "no_v_some_p": 0, "no_v_some_p_fraction": 0.0,
                "all_v_no_p": 0, "all_v_no_p_fraction": 0.0,
                "some_v_no_p": 0, "some_v_no_p_fraction": 0.0,
            },
        ]

    @mock.patch('common.clients.CourseStructureApiClient.course_structures', create=True)
    @mock.patch('analyticsclient.course.Course.typology')
    def test_presenter(self, mock_raw_typology_data, mock_structures):
        mock_raw_typology_data.return_value = self.get_mock_input_data_from_api()
        mock_structures.return_value.get = self.get_mock_course_structure

        typology_data, last_updated = self.presenter.get_data()

        self.assertEqual(typology_data, self.get_expected_data())
        self.assertEqual(last_updated, self.presenter.parse_api_datetime(self.created_date))


class CourseEngagementVideoPresenterTests(SwitchMixin, TestCase):
    SECTION_ID = 'i4x://edX/DemoX/chapter/9fca584977d04885bc911ea76a9ef29e'
    SUBSECTION_ID = 'i4x://edX/DemoX/sequential/07bc32474380492cb34f76e5f9d9a135'
    VIDEO_ID = 'i4x://edX/DemoX/video/0b9e39477cf34507a7a48f74be381fdd'

    def setUp(self):
        super(CourseEngagementVideoPresenterTests, self).setUp()
        self.course_id = 'this/course/id'
        self.presenter = CourseEngagementVideoPresenter(None, self.course_id)

    def test_default_block_data(self):
        self.assertDictEqual(self.presenter.default_block_data, {
            'users_at_start': 0,
            'users_at_end': 0,
            'end_percent': 0,
            'start_only_users': 0,
            'start_only_percent': 0,
        })

    def test_module_id_to_data_id(self):
        opaque_key_id = 'i4x-edX-DemoX-video-0b9e39477cf34507a7a48f74be381fdd'
        module_id = 'i4x://edX/DemoX/video/0b9e39477cf34507a7a48f74be381fdd'
        self.assertEqual(self.presenter.module_id_to_data_id({'id': module_id}), opaque_key_id)

        block_id = 'block-v1:edX+DemoX.1+2014+type@problem+block@466f474fa4d045a8b7bde1b911e095ca'
        self.assertEqual(self.presenter.module_id_to_data_id({'id': block_id}), '466f474fa4d045a8b7bde1b911e095ca')

    def test_post_process_adding_data_to_blocks(self):
        def url_func(parent_block, child_block):
            return '{}-{}'.format(parent_block, child_block)
        user_data = {'users_at_start': 10}
        self.presenter.post_process_adding_data_to_blocks(user_data, 'parent', 'child', url_func)
        self.assertDictContainsSubset({'url': 'parent-child'}, user_data)

        empty_data = {}
        self.presenter.post_process_adding_data_to_blocks(empty_data, 'parent', 'child', None)
        self.assertDictEqual({}, empty_data)

    def test_build_module_url_func(self):
        url_func = self.presenter.build_module_url_func(self.SECTION_ID)
        actual_url = url_func({'id': self.SUBSECTION_ID},
                              {'id': self.VIDEO_ID})
        expected_url = reverse('courses:engagement:video_timeline',
                               kwargs={
                                   'course_id': self.course_id,
                                   'section_id': self.SECTION_ID,
                                   'subsection_id': self.SUBSECTION_ID,
                                   'video_id': self.VIDEO_ID
                               })
        self.assertEqual(actual_url, expected_url)

    def test_build_subsection_url_func(self):
        url_func = self.presenter.build_subsection_url_func(self.SECTION_ID)
        actual_url = url_func({'id': self.SUBSECTION_ID})
        expected_url = reverse('courses:engagement:video_subsection',
                               kwargs={
                                   'course_id': self.course_id,
                                   'section_id': self.SECTION_ID,
                                   'subsection_id': self.SUBSECTION_ID,
                               })
        self.assertEqual(actual_url, expected_url)

    def test_build_section_url_func(self):
        actual_url = self.presenter.build_section_url({'id': self.SECTION_ID})
        expected_url = reverse('courses:engagement:video_section',
                               kwargs={
                                   'course_id': self.course_id,
                                   'section_id': self.SECTION_ID,
                               })
        self.assertEqual(actual_url, expected_url)

    def test_attach_computed_data(self):
        max_users = 15
        start_only_users = 10
        end_users = max_users - start_only_users
        end_percent = end_users / max_users
        module_data = {
            'encoded_module_id': self.VIDEO_ID,
            'users_at_start': max_users,
            'users_at_end': end_users
        }
        self.presenter.attach_computed_data(module_data)
        self.assertDictEqual(module_data, {
            'id': self.VIDEO_ID,
            'users_at_start': max_users,
            'users_at_end': end_users,
            'end_percent': end_percent,
            'start_only_users': start_only_users,
            'start_only_percent': start_only_users / max_users,
        })

    def test_attach_aggregated_data_to_parent(self):
        parent = {
            'num_modules': 2,
            'children': [
                {
                    'users_at_start': 60,
                    'users_at_end': 40,
                },
                {
                    'users_at_start': 0,
                    'users_at_end': 0,
                },
            ]
        }
        expected = copy.deepcopy(parent)
        expected.update({
            'users_at_start': 60,
            'users_at_end': 40,
            'index': 1,
            'average_users_at_start': 30,
            'average_users_at_end': 20,
            'end_percent': 2/3,
            'start_only_users': 20,
            'start_only_percent': 1/3,
        })

        self.presenter.attach_aggregated_data_to_parent(0, parent)
        self.assertDictEqual(parent, expected)

    @mock.patch('analyticsclient.course.Course.videos')
    def test_fetch_course_module_data(self, mock_videos):
        videos = [
            {
                "pipeline_video_id": "edX/DemoX/Demo_Course|i4x-edX-DemoX-video-7e9b434e6de3435ab99bd3fb25bde807",
                "encoded_module_id": "i4x-edX-DemoX-video-7e9b434e6de3435ab99bd3fb25bde807",
                "duration": 257,
                "segment_length": 5,
                "users_at_start": 10,
                "users_at_end": 0,
                "created": "2015-04-15T214158"
            },
            {
                "pipeline_video_id": "edX/DemoX/Demo_Course|i4x-edX-DemoX-videoalpha-0b9e39477cf34507a7a48f74be381fdd",
                "encoded_module_id": "i4x-edX-DemoX-videoalpha-0b9e39477cf34507a7a48f74be381fdd",
                "duration": 195,
                "segment_length": 5,
                "users_at_start": 55,
                "users_at_end": 0,
                "created": "2015-04-15T214158"
            }
        ]
        mock_videos.return_value = videos
        self.assertListEqual(self.presenter.fetch_course_module_data(), videos)

        mock_videos.side_effect = NoVideosError(course_id=self.course_id)
        with self.assertRaises(NoVideosError):
            self.presenter.fetch_course_module_data()

    @mock.patch('analyticsclient.module.Module.video_timeline')
    def test_get_video_timeline(self, mock_timeline):
        factory = CourseEngagementDataFactory()
        video_module = {
            'pipeline_video_id': 'edX/DemoX/Demo_Course|i4x-edX-DemoX-videoalpha-0b9e39477cf34507a7a48f74be381fdd',
            'segment_length': 5,
            'duration': None
        }
        # duration can be null/None
        mock_timeline.return_value = factory.get_video_timeline_api_response()
        actual_timeline = self.presenter.get_video_timeline(video_module)
        expected_timeline = factory.get_presented_video_timeline(duration=495)
        self.assertEqual(100, len(actual_timeline))
        self.assertTimeline(expected_timeline, actual_timeline)

        video_module['duration'] = 499
        mock_timeline.return_value = factory.get_video_timeline_api_response()
        actual_timeline = self.presenter.get_video_timeline(video_module)
        last_segment = expected_timeline[-1].copy()
        last_segment.update({
            'segment': last_segment['segment'] + 1,
            'start_time': video_module['duration']
        })
        expected_timeline.append(last_segment)
        self.assertEqual(101, len(actual_timeline))
        self.assertTimeline(expected_timeline, actual_timeline)

        video_module['duration'] = 501
        expected_timeline[-1].update({
            'start_time': 500,
            'num_users': 0,
            'num_views': 0,
            'num_replays': 0
        })
        last_segment = expected_timeline[-1].copy()
        last_segment.update({
            'segment': last_segment['segment'] + 1,
            'start_time': video_module['duration']
        })
        expected_timeline.append(last_segment)
        mock_timeline.return_value = factory.get_video_timeline_api_response()
        actual_timeline = self.presenter.get_video_timeline(video_module)
        self.assertEqual(102, len(actual_timeline))
        self.assertTimeline(expected_timeline, actual_timeline)

    def assertTimeline(self, expected_timeline, actual_timeline):
        self.assertEqual(len(expected_timeline), len(actual_timeline))
        for expected, actual in zip(expected_timeline, actual_timeline):
            self.assertDictContainsSubset(actual, expected)

    def test_build_live_url(self):
        actual_view_live_url = self.presenter.build_view_live_url('a-url', self.VIDEO_ID)
        self.assertEqual('a-url/{}/jump_to/{}'.format(self.course_id, self.VIDEO_ID), actual_view_live_url)
        self.assertEqual(None, self.presenter.build_view_live_url(None, self.VIDEO_ID))


class CourseEnrollmentPresenterTests(SwitchMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toggle_switch('display_verified_enrollment', True)

    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.presenter = CourseEnrollmentPresenter(self.course_id)

    @mock.patch('analyticsclient.course.Course.enrollment', mock.Mock(return_value=[]))
    def test_get_trend_summary_no_data(self):
        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        expected_summary = {
            'last_updated': None,
            'current_enrollment': None,
            'total_enrollment': None,
            'enrollment_change_last_7_days': None,
        }

        self.assertDictEqual(actual_summary, expected_summary)
        self.assertEqual(actual_trend, [])

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data(self, mock_enrollment):
        mock_enrollment.return_value = utils.get_mock_api_enrollment_data(self.course_id)

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_enrollment_summary())

        expected_trend = utils.get_mock_presenter_enrollment_trend(self.course_id)
        self.assertListEqual(actual_trend, expected_trend)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data_with_gaps(self, mock_enrollment):
        """
        If the API returns data with gaps, get_summary_and_trend_data should fill in those gaps with data from the
        previous day.
        """
        gaps = utils.get_mock_api_enrollment_data_with_gaps(self.course_id)
        mock_enrollment.return_value = gaps

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_enrollment_summary())

        expected_trend = utils.get_mock_presenter_enrollment_trend_with_gaps_filled(self.course_id)
        self.assertListEqual(actual_trend, expected_trend)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_summary_and_trend_data_small(self, mock_enrollment):
        """
        Verify the presenter responds appropriately when the course has a limited amount of data (e.g. one data point).
        """
        mock_enrollment.return_value = utils.get_mock_api_enrollment_data(self.course_id)[-1:]

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_presenter_enrollment_summary_small())
        self.assertListEqual(actual_trend, utils.get_mock_presenter_enrollment_data_small(self.course_id))

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_geography_data(self, mock_enrollment):
        mock_enrollment.return_value = utils.get_mock_api_enrollment_geography_data(self.course_id)

        expected_summary, expected_data = utils.get_mock_presenter_enrollment_geography_data()
        summary, actual_data = self.presenter.get_geography_data()

        self.assertDictEqual(summary, expected_summary)
        self.assertListEqual(actual_data, expected_data)

        # test with a small set of countries
        mock_data = utils.get_mock_api_enrollment_geography_data_limited(self.course_id)
        mock_enrollment.return_value = mock_data

        expected_summary, expected_data = utils.get_mock_presenter_enrollment_geography_data_limited()
        summary, actual_data = self.presenter.get_geography_data()

        self.assertDictEqual(summary, expected_summary)
        self.assertListEqual(actual_data, expected_data)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_hide_empty_enrollment_modes(self, mock_enrollment):
        """ Enrollment modes with no enrolled students should not be returned. """
        mock_enrollment.return_value = utils.get_mock_api_enrollment_data(self.course_id, include_verified=False)

        actual_summary, actual_trend = self.presenter.get_summary_and_trend_data()
        self.assertDictEqual(actual_summary, utils.get_mock_enrollment_summary(include_verified=False))

        expected_trend = utils.get_mock_presenter_enrollment_trend(self.course_id, include_verified=False)
        self.assertListEqual(actual_trend, expected_trend)


class CourseEnrollmentDemographicsPresenterTests(TestCase):
    def setUp(self):
        self.course_id = 'edX/DemoX/Demo_Course'
        self.presenter = CourseEnrollmentDemographicsPresenter(self.course_id)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_gender(self, mock_gender):
        mock_data = utils.get_mock_api_enrollment_gender_data(self.course_id)
        mock_gender.return_value = mock_data

        last_updated, gender_data, trend, known_percent = self.presenter.get_gender()
        self.assertEqual(last_updated, utils.CREATED_DATETIME)
        self.assertListEqual(gender_data, utils.get_presenter_enrollment_gender_data())
        self.assertListEqual(trend, utils.get_presenter_enrollment_gender_trend(self.course_id))
        self.assertEqual(known_percent, 0.5)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_ages(self, mock_age):
        mock_data = utils.get_mock_api_enrollment_age_data(self.course_id)
        mock_age.return_value = mock_data

        last_updated, summary, binned_ages, known_percent = self.presenter.get_ages()

        self.assertEqual(last_updated, utils.CREATED_DATETIME)
        self.assertDictEqual(summary, utils.get_presenter_enrollment_ages_summary())
        self.assertListEqual(binned_ages, utils.get_presenter_enrollment_binned_ages())
        self.assertEqual(known_percent, 0.5)

    @mock.patch('analyticsclient.course.Course.enrollment')
    def test_get_education(self, mock_education):
        mock_data = utils.get_mock_api_enrollment_education_data(self.course_id)
        mock_education.return_value = mock_data

        last_updated, education_summary, education_levels, known_percent = self.presenter.get_education()

        self.assertEqual(last_updated, utils.CREATED_DATETIME)
        self.assertDictEqual(education_summary, utils.get_mock_presenter_enrollment_education_summary())
        self.assertListEqual(education_levels, utils.get_mock_presenter_enrollment_education_data())
        self.assertEqual(known_percent, 0.5)


PERFORMER_PRESENTER_COURSE_ID = 'edX/DemoX/Demo_Course'


class ListWithName(list):
    pass


def annotated(l, name):
    alist = ListWithName(l)
    setattr(alist, '__name__', name)
    return alist


@ddt
class CoursePerformancePresenterTests(TestCase):

    def setUp(self):
        cache.clear()
        self.course_id = PERFORMER_PRESENTER_COURSE_ID
        self.problem_id = 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36'
        self.presenter = CoursePerformancePresenter(None, self.course_id)
        self.factory = CoursePerformanceDataFactory()

    # First and last response counts were added, insights can handle both types of API responses at the moment.
    @data(
        annotated(
            utils.get_mock_api_answer_distribution_multiple_questions_data(PERFORMER_PRESENTER_COURSE_ID),
            'count'
        ),
        annotated(
            utils.get_mock_api_answer_distribution_multiple_questions_first_last_data(PERFORMER_PRESENTER_COURSE_ID),
            'first_last'
        ),
    )
    @mock.patch('analyticsclient.module.Module.answer_distribution')
    def test_multiple_answer_distribution(self, mock_data, mock_answer_distribution):
        mock_answer_distribution.reset_mock()
        mock_answer_distribution.return_value = mock_data

        problem_parts = [
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
                'expected': {
                    'active_question': 'Submissions for Part 1: Is this a text problem?',
                    'problem_part_description': 'Part 1: Is this a text problem?',
                    'is_random': False,
                    'answer_type': 'text'
                }
            },
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1',
                'expected': {
                    'active_question': 'Submissions for Part 2: Is this a numeric problem?',
                    'problem_part_description': 'Part 2: Is this a numeric problem?',
                    'is_random': False,
                    'answer_type': 'numeric'
                }
            },
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_4_1',
                'expected': {
                    'active_question': 'Submissions for Part 3: Is this a randomized problem?',
                    'problem_part_description': 'Part 3: Is this a '
                                                'randomized problem?',
                    'is_random': True,
                    'answer_type': 'numeric'
                }
            }
        ]
        questions = utils.get_presenter_performance_answer_distribution_multiple_questions()
        self.assertAnswerDistribution(problem_parts, questions, mock_data)

    @mock.patch('analyticsclient.module.Module.answer_distribution')
    def test_single_answer_distribution(self, mock_answer_distribution):

        mock_data = utils.get_mock_api_answer_distribution_single_question_data(self.course_id)
        mock_answer_distribution.return_value = mock_data

        problem_parts = [
            {
                'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
                'expected': {
                    'active_question': 'Submissions: Is this a text problem?',
                    'problem_part_description': 'Is this a text problem?',
                    'is_random': False,
                    'answer_type': 'text'
                }
            }
        ]
        questions = utils.get_presenter_performance_answer_distribution_single_question()
        self.assertAnswerDistribution(problem_parts, questions, mock_data)

    def assertAnswerDistribution(self, expected_problem_parts, expected_questions, answer_distribution_data):
        for part in expected_problem_parts:
            expected = part['expected']
            answer_distribution_entry = self.presenter.get_answer_distribution(self.problem_id, part['part_id'])
            self.assertEqual(answer_distribution_entry.last_updated, utils.CREATED_DATETIME)
            self.assertListEqual(answer_distribution_entry.questions, expected_questions)
            self.assertEqual(answer_distribution_entry.problem_part_description, expected['problem_part_description'])
            self.assertEqual(answer_distribution_entry.active_question, expected['active_question'])
            self.assertEqual(answer_distribution_entry.answer_type, expected['answer_type'])
            self.assertEqual(answer_distribution_entry.is_random, expected['is_random'])

            expected_answer_distribution = [d for d in answer_distribution_data if d['part_id'] == part['part_id']]
            self.assertListEqual(answer_distribution_entry.answer_distribution, expected_answer_distribution)
            if answer_distribution_entry.is_random:
                self.assertIsNone(answer_distribution_entry.answer_distribution_limited)
            else:
                self.assertListEqual(answer_distribution_entry.answer_distribution_limited,
                                     expected_answer_distribution[:12])

    @mock.patch('slumber.Resource.get', mock.Mock(return_value=CoursePerformanceDataFactory.grading_policy))
    def test_grading_policy(self):
        """
        Verify the presenter returns the correct grading policy.

        Empty (non-truthy) assignment types should be dropped.
        """

        grading_policy = self.presenter.grading_policy()
        self.assertListEqual(grading_policy, self.factory.presented_grading_policy)

        percent = self.presenter.get_max_policy_display_percent(grading_policy)
        self.assertEqual(100, percent)

        percent = self.presenter.get_max_policy_display_percent([{'weight': 0.0}, {'weight': 1.0}, {'weight': 0.04}])
        self.assertEqual(90, percent)

    def test_assignment_types(self):
        """ Verify the presenter returns the correct assignment types. """
        with mock.patch('courses.presenters.performance.CoursePerformancePresenter.grading_policy',
                        mock.Mock(return_value=self.factory.presented_grading_policy)):
            self.assertListEqual(self.presenter.assignment_types(), self.factory.presented_assignment_types)

    def test_assignments(self):
        """ Verify the presenter returns the correct assignments and sets the last updated date. """

        self.assertIsNone(self.presenter.last_updated)

        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            with mock.patch('analyticsclient.course.Course.problems', self.factory.problems):
                # With no assignment type set, the method should return all assignment types.
                assignments = self.presenter.assignments()
                expected_assignments = self.factory.presented_assignments

                self.assertListEqual(assignments, expected_assignments)
                self.assertEqual(self.presenter.last_updated, utils.CREATED_DATETIME)

                # With an assignment type set, the presenter should return only the assignments of the specified type.
                for assignment_type in self.factory.presented_assignment_types:
                    cache.clear()
                    expected = [assignment for assignment in expected_assignments if
                                assignment[u'assignment_type'] == assignment_type['name']]

                    for index, assignment in enumerate(expected):
                        assignment[u'index'] = index + 1

                    self.assertListEqual(self.presenter.assignments(assignment_type), expected)

    def test_assignment(self):
        """ Verify the presenter returns a specific assignment. """
        with mock.patch('courses.presenters.performance.CoursePerformancePresenter.assignments',
                        mock.Mock(return_value=self.factory.presented_assignments)):
            # The method should return None if the assignment does not exist.
            self.assertIsNone(self.presenter.assignment(None))
            self.assertIsNone(self.presenter.assignment('non-existent-id'))

            # The method should return an individual assignment if the ID exists.
            assignment = self.factory.presented_assignments[0]
            self.assertDictEqual(self.presenter.assignment(assignment[u'id']), assignment)

    def test_problem(self):
        """ Verify the presenter returns a specific problem. """
        problem = self.factory.presented_assignments[0]['children'][0]
        _id = problem['id']

        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            actual = self.presenter.block(_id)
            expected = {
                'id': _id,
                'name': problem['name'],
                'children': []
            }
            self.assertDictContainsSubset(expected, actual)

    def test_sections(self):
        """ Verify the presenter returns a specific assignment. """
        ungraded_problems = self.factory.problems(False)
        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            with mock.patch('analyticsclient.course.Course.problems', mock.Mock(return_value=ungraded_problems)):
                expected = self.factory.presented_sections
                self.assertListEqual(self.presenter.sections(), expected)

    def test_section(self):
        """ Verify the presenter returns a specific assignment. """
        ungraded_problems = self.factory.problems(False)
        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            with mock.patch('analyticsclient.course.Course.problems', mock.Mock(return_value=ungraded_problems)):
                # The method should return None if the assignment does not exist.
                self.assertIsNone(self.presenter.section(None))
                self.assertIsNone(self.presenter.section('non-existent-id'))
                expected = self.factory.presented_sections[0]
                self.assertEqual(self.presenter.section(expected['id']), expected)

    def test_subsections(self):
        """ Verify the presenter returns a specific assignment. """
        ungraded_problems = self.factory.problems(False)
        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            with mock.patch('analyticsclient.course.Course.problems', mock.Mock(return_value=ungraded_problems)):
                # The method should return None if the assignment does not exist.
                self.assertIsNone(self.presenter.subsections(None))
                self.assertIsNone(self.presenter.subsections('non-existent-id'))
                section = self.factory.presented_sections[0]
                expected = section['children']
                self.assertListEqual(self.presenter.subsections(section['id']), expected)

    def test_subsection(self):
        """ Verify the presenter returns a specific assignment. """
        ungraded_problems = self.factory.problems(False)
        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            with mock.patch('analyticsclient.course.Course.problems', mock.Mock(return_value=ungraded_problems)):
                # The method should return None if the assignment does not exist.
                self.assertIsNone(self.presenter.subsection(None, None))
                self.assertIsNone(self.presenter.subsection('non-existent-id', 'nope'))
                section = self.factory.presented_sections[0]
                expected_subsection = section['children'][0]
                self.assertEqual(self.presenter.subsection(section['id'], expected_subsection['id']),
                                 expected_subsection)

    def test_subsection_problems(self):
        """ Verify the presenter returns a specific assignment. """
        ungraded_problems = self.factory.problems(False)
        with mock.patch('slumber.Resource.get', mock.Mock(return_value=self.factory.structure)):
            with mock.patch('analyticsclient.course.Course.problems', mock.Mock(return_value=ungraded_problems)):
                # The method should return None if the assignment does not exist.
                self.assertIsNone(self.presenter.subsection_children(None, None))
                self.assertIsNone(self.presenter.subsection_children('non-existent-id', 'nope'))
                section = self.factory.presented_sections[0]
                subsection = section['children'][0]
                expected_problems = subsection['children']
                self.assertListEqual(
                    self.presenter.subsection_children(section['id'], subsection['id']), expected_problems)
