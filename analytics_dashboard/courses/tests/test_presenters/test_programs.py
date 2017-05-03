from ddt import (
    data,
    ddt,
    unpack
)
import mock

from django.test import (
    override_settings,
    TestCase
)

from courses.presenters.programs import ProgramsPresenter
from courses.tests.utils import CourseSamples, ProgramSamples, get_mock_programs


@ddt
class ProgramsPresenterTests(TestCase):
    def setUp(self):
        self.maxDiff = None
        super(ProgramsPresenterTests, self).setUp()

    @property
    def mock_api_response(self):
        '''
        Returns a mocked API response for programs including some null fields.
        '''
        return get_mock_programs()

    def get_expected_programs(self, program_ids=None, course_ids=None):
        ''''Expected results with default values, sorted, and filtered to program_ids.'''
        if program_ids is None:
            programs = self.mock_api_response
        else:
            programs = [program for program in self.mock_api_response if program['program_id'] in program_ids]

        if course_ids is None:
            filtered_programs = programs
        else:
            filtered_programs = []
            for program in programs:
                for course_id in course_ids:
                    if course_id in program['course_ids']:
                        filtered_programs.append(program)
                        break

        # fill in with defaults
        for program in filtered_programs:
            for field in ProgramsPresenter.NON_NULL_STRING_FIELDS:
                if program[field] is None:
                    program[field] = ''

        # sort by title
        return sorted(
            filtered_programs,
            key=lambda x: (not x['program_title'], x['program_title']))

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    # First element is the program_ids filter, second is the course_ids filter
    @data(
        [None, None],
        [[ProgramSamples.DEMO_PROGRAM_ID], None],
        [[ProgramSamples.DEMO_PROGRAM_ID, ProgramSamples.DEMO_PROGRAM2_ID], None],
        [None, [CourseSamples.DEMO_COURSE_ID]],
        [None, [CourseSamples.DEPRECATED_DEMO_COURSE_ID]],
        [None, [CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID]],
        [[ProgramSamples.DEMO_PROGRAM_ID], [CourseSamples.DEMO_COURSE_ID]],
        [[ProgramSamples.DEMO_PROGRAM2_ID], [CourseSamples.DEPRECATED_DEMO_COURSE_ID]],
        [[ProgramSamples.DEMO_PROGRAM_ID], [CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID]],
    )
    @unpack
    def test_get_programs(self, program_ids, course_ids):
        ''''Test programs filtered from API response.'''
        presenter = ProgramsPresenter()

        with mock.patch('analyticsclient.programs.Programs.programs',
                        mock.Mock(return_value=self.mock_api_response)):
            actual_programs = presenter.get_programs(program_ids=program_ids, course_ids=course_ids)
            self.assertListEqual(actual_programs, self.get_expected_programs(program_ids=program_ids,
                                                                             course_ids=course_ids))
