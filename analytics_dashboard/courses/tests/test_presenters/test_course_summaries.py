from ddt import (
    data,
    ddt
)
import mock

from django.test import (
    override_settings,
    TestCase
)

from courses.presenters.course_summaries import CourseSummariesPresenter
from courses.tests import utils
from courses.tests.utils import CourseSamples


@ddt
class CourseSummariesPresenterTests(TestCase):

    @property
    def mock_api_response(self):
        '''
        Returns a mocked API response for two courses including some null fields.
        '''
        return [{
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
            'enrollment_modes': {
                'audit': {
                    'count': 4,
                    'cumulative_count': 4,
                    'count_change_7_days': 4
                },
                'credit': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'verified': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'professional': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'honor': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                }
            },
            'created': utils.CREATED_DATETIME_STRING,
        }, {
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
            'enrollment_modes': {
                'audit': {
                    'count': 832,
                    'cumulative_count': 1007,
                    'count_change_7_days': 0
                },
                'credit': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'verified': {
                    'count': 12,
                    'cumulative_count': 12,
                    'count_change_7_days': 0
                },
                'professional': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'honor': {
                    'count': 3040,
                    'cumulative_count': 4087,
                    'count_change_7_days': 0
                }
            },
            'created': utils.CREATED_DATETIME_STRING,
        }, {
            'course_id': 'another/course/id',
            'catalog_course_title': None,
            'catalog_course': None,
            'start_date': None,
            'end_date': None,
            'pacing_type': None,
            'availability': None,
            'count': 1,
            'cumulative_count': 1,
            'count_change_7_days': 0,
            'enrollment_modes': {
                'audit': {
                    'count': 1,
                    'cumulative_count': 1,
                    'count_change_7_days': 0
                },
                'credit': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'verified': {
                    'count': 1,
                    'cumulative_count': 1,
                    'count_change_7_days': 0
                },
                'professional': {
                    'count': 0,
                    'cumulative_count': 0,
                    'count_change_7_days': 0
                },
                'honor': {
                    'count': 1,
                    'cumulative_count': 1,
                    'count_change_7_days': 0
                }
            },
            'created': utils.CREATED_DATETIME_STRING,
        }]

    def get_expected_summaries(self, course_ids=None):
        ''''Expected results with default values, sorted, and filtered to course_ids.'''
        if course_ids is None:
            course_ids = [CourseSamples.DEMO_COURSE_ID,
                          CourseSamples.DEPRECATED_DEMO_COURSE_ID,
                          'another/course/id']

        summaries = [summary for summary in self.mock_api_response if summary['course_id'] in course_ids]

        # fill in with defaults
        for summary in summaries:
            for field in CourseSummariesPresenter.NON_NULL_STRING_FIELDS:
                if summary[field] is None:
                    summary[field] = ''

        # sort by title
        return sorted(
            summaries,
            key=lambda x: (x['catalog_course_title'] is not None, x['catalog_course_title']))

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    @data(
        None,
        [CourseSamples.DEMO_COURSE_ID],
        [CourseSamples.DEPRECATED_DEMO_COURSE_ID],
        [CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID],
    )
    def test_get_summaries(self, course_ids):
        ''''Test courses filtered from API response.'''
        presenter = CourseSummariesPresenter()

        with mock.patch('analyticsclient.course_summaries.CourseSummaries.course_summaries',
                        mock.Mock(return_value=self.mock_api_response)):
            actual_summaries, last_updated = presenter.get_course_summaries(course_ids=course_ids)
            self.assertListEqual(actual_summaries, self.get_expected_summaries(course_ids))
            self.assertEqual(last_updated, utils.CREATED_DATETIME)
