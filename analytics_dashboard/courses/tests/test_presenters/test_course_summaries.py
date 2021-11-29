import unittest.mock as mock

from analyticsclient.client import Client
from ddt import data, ddt, unpack
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from analytics_dashboard.courses.presenters.course_summaries import CourseSummariesPresenter
from analytics_dashboard.courses.tests import utils
from analytics_dashboard.courses.tests.utils import CourseSamples

_ANOTHER_DEPRECATED_COURSE_ID = 'another/course/id'


@ddt
class CourseSummariesPresenterTests(TestCase):

    _API_SUMMARIES = {
        CourseSamples.DEPRECATED_DEMO_COURSE_ID: {
            'course_id': CourseSamples.DEPRECATED_DEMO_COURSE_ID,
            'catalog_course_title': 'Deprecated demo course',
            'catalog_course': 'edX+demo.1x',
            'start_date': '2016-03-07T050000',
            'end_date': '2016-04-18T080000',
            'pacing_type': 'instructor_paced',
            'availability': 'Archived',
            'count': 4,
            'cumulative_count': 4,
            'count_change_7_days': 4,
            'passing_users': 2,
            'enrollment_modes': {
                'audit': {
                    'count': 4,
                    'cumulative_count': 4,
                    'count_change_7_days': 4,
                    'passing_users': 2,
                },
                'credit': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'verified': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'professional': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'honor': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                }
            },
            'created': utils.CREATED_DATETIME_STRING,
        },
        CourseSamples.DEMO_COURSE_ID: {
            'course_id': CourseSamples.DEMO_COURSE_ID,
            'catalog_course_title': 'Demo Course',
            'catalog_course': None,
            'start_date': None,
            'end_date': None,
            'pacing_type': None,
            'availability': None,
            'count': 3884,
            'cumulative_count': 5106,
            'count_change_7_days': 0,
            'passing_users': 912,
            'enrollment_modes': {
                'audit': {
                    'count': 832,
                    'cumulative_count': 1007,
                    'count_change_7_days': 0,
                    'passing_users': 800,
                },
                'credit': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'verified': {
                    'count': 12,
                    'cumulative_count': 12,
                    'count_change_7_days': 0,
                    'passing_users': 12,
                },
                'professional': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'honor': {
                    'count': 3040,
                    'cumulative_count': 4087,
                    'count_change_7_days': 0,
                    'passing_users': 100,
                },
                'masters': {
                    'count': 1101,
                    'cumulative_count': 1103,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                }
            },
            'created': utils.CREATED_DATETIME_STRING,
        },
        _ANOTHER_DEPRECATED_COURSE_ID: {
            'course_id': _ANOTHER_DEPRECATED_COURSE_ID,
            'catalog_course_title': None,
            'catalog_course': None,
            'start_date': None,
            'end_date': None,
            'pacing_type': 'instructor_paced',
            'availability': None,
            'count': 0,
            'cumulative_count': 1,
            'count_change_7_days': 0,
            'enrollment_modes': {
                'audit': {
                    'count': 1,
                    'cumulative_count': 1,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'credit': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'verified': {
                    'count': 1,
                    'cumulative_count': 1,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'professional': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'honor': {
                    'count': 1,
                    'cumulative_count': 1,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                },
                'masters': {
                    'count': 10,
                    'cumulative_count': 10,
                    'count_change_7_days': 0,
                    'passing_users': 0,
                }
            },
            'created': utils.CREATED_DATETIME_STRING,
        },
    }

    _PRESENTER_SUMMARIES = {
        CourseSamples.DEPRECATED_DEMO_COURSE_ID:
            _API_SUMMARIES[CourseSamples.DEPRECATED_DEMO_COURSE_ID],
        CourseSamples.DEMO_COURSE_ID:
            _API_SUMMARIES[CourseSamples.DEMO_COURSE_ID],
        _ANOTHER_DEPRECATED_COURSE_ID:
            _API_SUMMARIES[_ANOTHER_DEPRECATED_COURSE_ID],
    }
    _PRESENTER_SUMMARIES[CourseSamples.DEMO_COURSE_ID].update({
        'catalog_course': '',
        'start_date': '',
        'end_date': '',
        'pacing_type': '',
        'availability': '',
    })
    _PRESENTER_SUMMARIES[_ANOTHER_DEPRECATED_COURSE_ID].update({
        'catalog_course': '',
        'catalog_course_title': '',
        'start_date': '',
        'end_date': '',
        'availability': '',
    })

    @data(
        (
            None,
            [
                CourseSamples.DEMO_COURSE_ID,
                CourseSamples.DEPRECATED_DEMO_COURSE_ID,
                _ANOTHER_DEPRECATED_COURSE_ID,
            ],
        ),
        (
            [
                CourseSamples.DEPRECATED_DEMO_COURSE_ID,
                CourseSamples.DEMO_COURSE_ID,
            ],
            [
                CourseSamples.DEMO_COURSE_ID,
                CourseSamples.DEPRECATED_DEMO_COURSE_ID,
            ],
        ),
        (
            [
                CourseSamples.DEMO_COURSE_ID,
            ] * (settings.COURSE_SUMMARIES_IDS_CUTOFF + 1),  # tests filter_summaries
            [
                CourseSamples.DEMO_COURSE_ID,
            ],
        ),
    )
    @unpack
    def test_get_summaries(self, input_course_ids, ouptut_course_ids):
        presenter = CourseSummariesPresenter(Client('base_url'))
        if input_course_ids:
            mock_api_response = [
                self._API_SUMMARIES[course_id] for course_id in input_course_ids
            ]
        else:
            mock_api_response = list(self._API_SUMMARIES.values())
        expected_summaries = [
            self._PRESENTER_SUMMARIES[course_id] for course_id in ouptut_course_ids
        ]

        with mock.patch('analyticsclient.course_summaries.CourseSummaries.course_summaries',
                        mock.Mock(return_value=mock_api_response)):
            actual_summaries, last_updated = presenter.get_course_summaries(course_ids=input_course_ids)
            for actual, expected in zip(actual_summaries, expected_summaries):
                self.assertCountEqual(actual, expected)
            self.assertEqual(last_updated, utils.CREATED_DATETIME)

    def test_no_summaries(self):
        cache.clear()  # previous test has course_ids=None case cached
        presenter = CourseSummariesPresenter(Client('base_url'))
        with mock.patch('analyticsclient.course_summaries.CourseSummaries.course_summaries',
                        mock.Mock(return_value=[])):
            summaries, last_updated = presenter.get_course_summaries()
            self.assertListEqual(summaries, [])
            self.assertIsNone(last_updated)

    def test_get_course_summary_metrics(self):
        presenter = CourseSummariesPresenter(Client('base_url'))
        metrics = presenter.get_course_summary_metrics(self._PRESENTER_SUMMARIES.values())
        expected = {
            'total_enrollment': 5111,
            'current_enrollment': 3888,
            'enrollment_change_7_days': 4,
            'verified_enrollment': 13,
            'masters_enrollment': 1111,
        }
        self.assertEqual(metrics, expected)
