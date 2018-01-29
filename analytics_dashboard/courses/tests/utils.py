import StringIO
import copy
import csv
import datetime
import uuid

from analyticsclient.client import Client
from analyticsclient.constants import enrollment_modes, UNKNOWN_COUNTRY_CODE
import analyticsclient.constants.activity_type as AT
import analyticsclient.constants.education_level as EDUCATION_LEVEL
import analyticsclient.constants.gender as GENDER

from courses.permissions import set_user_course_permissions
from courses.presenters.performance import AnswerDistributionEntry
from courses.utils import get_encoded_module_id


CREATED_DATETIME = datetime.datetime(year=2014, month=2, day=2)
CREATED_DATETIME_STRING = CREATED_DATETIME.strftime(Client.DATETIME_FORMAT)
GAP_START = 2
GAP_END = 4


class CourseSamples(object):
    """Example course IDs for testing with."""
    DEMO_COURSE_ID = 'course-v1:edX+DemoX+Demo_2014'
    DEPRECATED_DEMO_COURSE_ID = 'edX/DemoX/Demo_Course'


class ProgramSamples(object):
    """Example program IDs for testing with."""
    DEMO_PROGRAM_ID = str(uuid.uuid4())
    DEMO_PROGRAM2_ID = str(uuid.uuid4())
    DEMO_PROGRAM3_ID = str(uuid.uuid4())
    DEMO_PROGRAM4_ID = str(uuid.uuid4())


def get_mock_api_enrollment_data(course_id):
    data = []
    start_date = datetime.date(year=2014, month=1, day=1)
    modes = enrollment_modes.ALL

    for index in range(31):
        date = start_date + datetime.timedelta(days=index)

        datum = {
            'date': date.strftime(Client.DATE_FORMAT),
            'course_id': unicode(course_id),
            'count': index * len(modes),
            'created': CREATED_DATETIME_STRING,
            'cumulative_count': index * len(modes) * 2
        }

        for mode in modes:
            datum[mode] = index

        data.append(datum)

    return data


def get_mock_api_enrollment_data_with_gaps(course_id):
    data = get_mock_api_enrollment_data(course_id)
    data[GAP_START:GAP_END] = []
    return data


def get_mock_enrollment_summary():
    summary = {
        'last_updated': CREATED_DATETIME,
        'current_enrollment': 150,
        'total_enrollment': 300,
        'enrollment_change_last_7_days': 35,
        'verified_enrollment': 30,
    }
    return summary


def get_mock_enrollment_summary_and_trend(course_id):
    return get_mock_enrollment_summary(), get_mock_presenter_enrollment_trend(course_id)


def _get_empty_enrollment(date):
    enrollment = {'count': 0, 'cumulative_count': 0, 'date': date}

    for mode in enrollment_modes.ALL:
        enrollment[mode] = 0

    return enrollment


def get_mock_presenter_enrollment_trend(course_id):
    trend = get_mock_api_enrollment_data(course_id)
    return trend


def parse_date(s):
    return datetime.datetime.strptime(s, Client.DATE_FORMAT).date()


def get_mock_presenter_enrollment_trend_with_gaps_filled(course_id):
    data = get_mock_presenter_enrollment_trend(course_id)
    data[GAP_START:GAP_END] = []

    datum = data[GAP_START - 1]

    for i in range(GAP_START, GAP_END):
        days = 1 + (i - GAP_START)
        item = copy.copy(datum)
        item['date'] = (parse_date(datum['date']) + datetime.timedelta(days=days)).strftime(Client.DATE_FORMAT)
        data.insert(i, item)

    return data


def get_mock_presenter_enrollment_data_small(course_id):
    data = [_get_empty_enrollment('2014-01-30'), get_mock_api_enrollment_data(course_id)[-1]]
    return data


def get_mock_presenter_enrollment_summary_small():
    summary = get_mock_enrollment_summary()
    summary['enrollment_change_last_7_days'] = None
    return summary


def get_mock_api_enrollment_geography_data(course_id):
    data = []
    items = ((u'USA', u'United States', 500), (None, UNKNOWN_COUNTRY_CODE, 300),
             (u'GER', u'Germany', 100), (u'CAN', u'Canada', 100))
    for item in items:
        data.append({'date': '2014-01-01', 'course_id': unicode(course_id), 'count': item[2],
                     'country': {'alpha3': item[0], 'name': item[1]}, 'created': CREATED_DATETIME_STRING})

    return data


def get_mock_api_enrollment_geography_data_limited(course_id):
    data = get_mock_api_enrollment_geography_data(course_id)
    return data[0:1]


def get_mock_presenter_enrollment_geography_data():
    data = [
        {'countryCode': 'USA', 'countryName': 'United States', 'count': 500, 'percent': 0.5},
        {'countryCode': 'GER', 'countryName': 'Germany', 'count': 100, 'percent': 0.1},
        {'countryCode': 'CAN', 'countryName': 'Canada', 'count': 100, 'percent': 0.1},
        {'countryCode': None, 'countryName': 'Unknown Country', 'count': 300, 'percent': 0.3},
    ]
    summary = {
        'last_updated': CREATED_DATETIME,
        'num_countries': 3,
        'top_countries': data[:3]  # The unknown entry is excluded from the list of top countries.
    }

    # Sort so that the unknown entry is in the correct location within the list.
    data = sorted(data, key=lambda i: i['count'], reverse=True)

    return summary, data


def get_mock_presenter_enrollment_geography_data_limited():
    """ Returns a smaller set of countries. """

    summary, data = get_mock_presenter_enrollment_geography_data()
    data = data[0:1]
    data[0]['percent'] = 1.0
    summary.update({
        'num_countries': 1,
        'top_countries': data
    })
    return summary, data


def get_mock_api_enrollment_gender_data(course_id):
    # top three are used in the summary (unknown is excluded)
    data = [
        {
            'course_id': course_id,
            'other': 123,
            GENDER.FEMALE: 456,
            GENDER.MALE: 789,
            GENDER.UNKNOWN: 1000,
            'date': '2014-09-21',
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'other': 500,
            GENDER.FEMALE: 100,
            GENDER.MALE: 400,
            GENDER.UNKNOWN: 1000,
            'date': '2014-09-22',
            'created': CREATED_DATETIME_STRING
        }
    ]

    return data


def get_presenter_enrollment_gender_data():
    return [
        {'gender': 'Female', 'percent': 0.1, 'order': 0},
        {'gender': 'Male', 'percent': 0.4, 'order': 1},
        {'gender': 'Other', 'percent': 0.5, 'order': 2}
    ]


def get_presenter_enrollment_gender_trend(course_id):
    return [
        {'course_id': course_id, GENDER.OTHER: 123, GENDER.FEMALE: 456, GENDER.MALE: 789, GENDER.UNKNOWN: 1000,
         'date': '2014-09-21', 'total': 2368,
         'created': CREATED_DATETIME_STRING},
        {'course_id': course_id, GENDER.OTHER: 500, GENDER.FEMALE: 100, GENDER.MALE: 400, GENDER.UNKNOWN: 1000,
         'date': '2014-09-22', 'total': 2000,
         'created': CREATED_DATETIME_STRING}
    ]


def get_presenter_gender(course_id):
    return CREATED_DATETIME, get_presenter_enrollment_gender_data(), get_presenter_enrollment_gender_trend(
        course_id), 0.5


def get_mock_api_enrollment_age_data(course_id):
    current_year = datetime.date.today().year
    data = [
        {'course_id': course_id, 'birth_year': current_year-150, 'count': 100, 'created': CREATED_DATETIME_STRING},
        {'course_id': course_id, 'birth_year': current_year-26, 'count': 400, 'created': CREATED_DATETIME_STRING},
        {'course_id': course_id, 'birth_year': current_year, 'count': 500, 'created': CREATED_DATETIME_STRING},
        {'course_id': course_id, 'birth_year': None, 'count': 1000, 'created': CREATED_DATETIME_STRING}
    ]

    return data


def get_presenter_enrollment_binned_ages():
    current_year = datetime.date.today().year
    oldest = current_year - 100
    binned = []

    for year in range(oldest, current_year + 1):
        binned.append({'age': current_year - year, 'count': 0, 'percent': 0})

    # adjust 100+
    binned[0]['count'] = 100
    binned[0]['percent'] = 0.05

    age_0_index = -1
    binned[age_0_index]['count'] = 500
    binned[age_0_index]['percent'] = 0.25

    # adjust year 2000
    age_26_index = -27
    binned[age_26_index]['count'] = 400
    binned[age_26_index]['percent'] = 0.2

    binned.insert(0, {'age': 'Unknown', 'count': 1000, 'percent': 0.5})

    return binned[::-1]


def get_presenter_enrollment_ages_summary():
    return {
        'median': 13.0,
        'age_25_and_under': 0.5,
        'age_26_to_40': 0.4,
        'age_41_and_over': 0.1
    }


def get_presenter_ages():
    return CREATED_DATETIME, get_presenter_enrollment_ages_summary(), get_presenter_enrollment_binned_ages(), 0.5


def get_mock_api_enrollment_education_data(course_id):
    data = [
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.NONE,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.OTHER,
            'count': 200,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.PRIMARY,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.JUNIOR_SECONDARY,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.SECONDARY,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.ASSOCIATES,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.BACHELORS,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.MASTERS,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': EDUCATION_LEVEL.DOCTORATE,
            'count': 100,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': course_id,
            'date': '2014-09-22',
            'education_level': None,
            'count': 1000,
            'created': CREATED_DATETIME_STRING
        },
    ]

    return data


def get_mock_presenter_enrollment_education_data():
    data = [
        {
            'educationLevel': 'None',
            'count': 100,
            'percent': 0.1,
            'order': 0
        },
        {
            'educationLevel': 'Primary',
            'count': 100,
            'percent': 0.1,
            'order': 1
        },
        {
            'educationLevel': 'Middle',
            'count': 100,
            'percent': 0.1,
            'order': 2
        },
        {
            'educationLevel': 'Secondary',
            'count': 100,
            'percent': 0.1,
            'order': 3
        },
        {
            'educationLevel': "Associate",
            'count': 100,
            'percent': 0.1,
            'order': 4
        },
        {
            'educationLevel': "Bachelor's",
            'count': 100,
            'percent': 0.1,
            'order': 5
        },
        {
            'educationLevel': "Master's",
            'count': 100,
            'percent': 0.1,
            'order': 6
        },
        {
            'educationLevel': 'Doctorate',
            'count': 100,
            'percent': 0.1,
            'order': 7
        },
        {
            'educationLevel': 'Other',
            'count': 200,
            'percent': 0.2,
            'order': 8
        },
        {
            'educationLevel': 'Unknown',
            'count': 1000
        }
    ]

    return data


def get_mock_presenter_enrollment_education_summary():
    return {
        'high_school_or_less': 0.3,
        'college': 0.2,
        'advanced': 0.2,
    }


def get_presenter_education():
    return (
        CREATED_DATETIME,
        get_mock_presenter_enrollment_education_summary(),
        get_mock_presenter_enrollment_education_data(),
        0.5
    )


def convert_list_of_dicts_to_csv(data, fieldnames=None):
    output = StringIO.StringIO()
    fieldnames = fieldnames or sorted(data[0].keys())

    writer = csv.DictWriter(output, fieldnames)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


def set_empty_permissions(user):
    set_user_course_permissions(user, [])
    return []


def mock_engagement_activity_summary_and_trend_data():
    trend = [
        {
            'weekEnding': '2013-01-08',
            AT.ANY: 100,
            AT.ATTEMPTED_PROBLEM: 301,
            AT.PLAYED_VIDEO: 1000,
            AT.POSTED_FORUM: 0,
        },
        {
            'weekEnding': '2013-01-01',
            AT.ANY: 1000,
            AT.ATTEMPTED_PROBLEM: 0,
            AT.PLAYED_VIDEO: 10000,
            AT.POSTED_FORUM: 45,
        }
    ]

    summary = {
        'last_updated': CREATED_DATETIME,
        AT.ANY: 100,
        AT.ATTEMPTED_PROBLEM: 301,
        AT.PLAYED_VIDEO: 1000,
        AT.POSTED_FORUM: 0,
    }

    return summary, trend


def get_mock_api_course_activity(course_id):
    return [
        {
            'course_id': unicode(course_id),
            'interval_end': '2014-09-01T000000',
            AT.ANY: 1000,
            AT.ATTEMPTED_PROBLEM: None,
            AT.PLAYED_VIDEO: 10000,
            AT.POSTED_FORUM: 45,
            'created': CREATED_DATETIME_STRING
        },
        {
            'course_id': unicode(course_id),
            'interval_end': '2014-09-08T000000',
            AT.ANY: 100,
            AT.ATTEMPTED_PROBLEM: 301,
            AT.PLAYED_VIDEO: 1000,
            AT.POSTED_FORUM: None,
            'created': CREATED_DATETIME_STRING
        },
    ]


# pylint: disable=unused-argument
def mock_course_activity(start_date=None, end_date=None):
    return get_mock_api_course_activity(u'edX/DemoX/Demo_Course')


# pylint: disable=unused-argument
def mock_course_activity_week_ahead(start_date=None, end_date=None):
    course_id = u'edX/DemoX/Demo_Course'
    activity = get_mock_api_course_activity(course_id)
    activity.append(
        {
            'course_id': unicode(course_id),
            'interval_end': '2014-09-15T000000',
            AT.ANY: 500,
            AT.ATTEMPTED_PROBLEM: 701,
            AT.PLAYED_VIDEO: 1500,
            AT.POSTED_FORUM: 32,
            'created': CREATED_DATETIME_STRING
        },
    )
    return activity


def get_mock_api_answer_distribution_multiple_questions_first_last_data(course_id):
    # First and last response counts were added, insights can handle both types of API responses at the moment.
    answers = get_mock_api_answer_distribution_multiple_questions_data(course_id)
    for answer in answers:
        answer['count'] = answer.pop('last_response_count')
        del answer['first_response_count']

    return answers


def get_mock_api_course_enrollment(course_id):
    """ Mock enrollment data corresponding to mock activity data above """
    aug = [{
        'course_id': course_id,
        'date': '2014-08-31',
        'count': 10000,
        'created': CREATED_DATETIME_STRING
    }]
    sept = [
        {
            'course_id': course_id,
            'date': '2014-09-{:02d}'.format(day),
            'count': 10000 + day,
            'created': CREATED_DATETIME_STRING
        }
        for day in range(1, 10)
    ]
    return aug + sept


# pylint: disable=unused-argument
def mock_course_enrollment(start_date=None, end_date=None):
    """ Mock API enrollment data """
    return get_mock_api_course_enrollment(u'edX/DemoX/Demo_Course')


def get_mock_api_answer_distribution_multiple_questions_data(course_id):
    answers = []
    total_first_count = 10
    total_last_count = 100

    for text_response in ['Asia', 'Europe', 'Africa']:
        answers.append({
            'answer_value': text_response,
            'correct': False,
            'first_response_count': total_first_count,
            'last_response_count': total_last_count,
            'course_id': course_id,
            'created': CREATED_DATETIME_STRING,
            'module_id': 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36',
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
            'value_id': 'choice_0',
            'variant': None,
            'problem_display_name': 'Example problem',
            'question_text': 'Is this a text problem?'
        })
        total_last_count = total_last_count - 1
        total_first_count = total_first_count + 1
    answers[0]['correct'] = True

    for numeric_value in range(20):
        answers.append({
            'answer_value': numeric_value,
            'correct': False,
            'first_response_count': total_first_count,
            'last_response_count': total_last_count,
            'course_id': course_id,
            'created': CREATED_DATETIME_STRING,
            'module_id': 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36',
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1',
            'value_id': None,
            'variant': None,
            'problem_display_name': 'Example problem',
            'question_text': 'Is this a numeric problem?'
        })
        total_last_count = total_last_count - 1
        total_first_count = total_first_count + 1
    answers[-1]['correct'] = True

    for randomized in range(5):
        answers.append({
            'answer_value': 0,
            'correct': True,
            'first_response_count': total_first_count,
            'last_response_count': total_last_count,
            'course_id': course_id,
            'created': CREATED_DATETIME_STRING,
            'module_id': 'i4x://edX/DemoX.1/problem/05d289c5ad3d47d48a77622c4a81ec36',
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_4_1',
            'value_id': None,
            'variant': randomized,
            'problem_display_name': 'Example problem',
            'question_text': 'Is this a randomized problem?'
        })
        total_last_count = total_last_count - 1
        total_first_count = total_first_count + 1

    return answers


def get_mock_api_answer_distribution_single_question_data(course_id):
    # get answers for one problem part
    return get_mock_api_answer_distribution_multiple_questions_data(course_id)[:3]


def get_presenter_performance_answer_distribution_multiple_questions():
    return [
        {
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
            'question': u'Submissions for Part 1: Is this a text problem?',
            'short_description': u'Part 1: Is this a text problem?',
            'problem_name': 'Example problem'
        },
        {
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_3_1',
            'question': u'Submissions for Part 2: Is this a numeric problem?',
            'short_description': u'Part 2: Is this a numeric problem?',
            'problem_name': 'Example problem'
        },
        {
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_4_1',
            'question': u'Submissions for Part 3: Is this a randomized problem?',
            'short_description': u'Part 3: Is this a randomized problem?',
            'problem_name': 'Example problem'
        }
    ]


def get_presenter_performance_answer_distribution_single_question():
    return [
        {
            'part_id': 'i4x-edX-DemoX_1-problem-5e3c6d6934494d87b3a025676c7517c1_2_1',
            'question': u'Submissions: Is this a text problem?',
            'short_description': u'Is this a text problem?',
            'problem_name': 'Example problem'
        }
    ]


def get_filtered_answer_distribution(course_id, problem_part_id):
    data = get_mock_api_answer_distribution_multiple_questions_data(course_id)
    return [d for d in data if d['part_id'] == problem_part_id]


def get_presenter_answer_distribution(course_id, problem_part_id):
    questions = get_presenter_performance_answer_distribution_multiple_questions()
    active_question = [i for i in questions if i['part_id'] == problem_part_id][0]['question']
    answer_distributions = get_filtered_answer_distribution(course_id, problem_part_id)
    answer_distribution_limited = answer_distributions[:12]
    is_random = answer_distribution_limited[0]['variant'] is not None
    try:
        float(answer_distribution_limited[0]['answer_value'])
        answer_type = 'numeric'
    except ValueError:
        answer_type = 'text'
    problem_part_description = 'Submissions for Part 1: Is this a text problem?'

    return AnswerDistributionEntry(CREATED_DATETIME, questions, active_question, answer_distributions,
                                   answer_distribution_limited, is_random, answer_type, problem_part_description)


def mock_course_name(course_id):
    return 'Test ' + course_id


def get_mock_video_data(course_fixture, excluded_module_ids=None):
    """
    Given a `course_fixture` (instance of `CourseFixture`), return a
    list of mock video data for each video in the course.

    If `excluded_module_ids` is provided, don't generate data for any
    module IDs in the list.
    """
    if excluded_module_ids is None:
        excluded_module_ids = list()
    return [
        {
            "pipeline_video_id": '{org}/{course}/{run}|{encoded_module_id}'.format(
                org=course_fixture.org, course=course_fixture.course, run=course_fixture.run,
                encoded_module_id=get_encoded_module_id(module_id)
            ),
            "encoded_module_id": get_encoded_module_id(module_id),
            "duration": 129,
            "segment_length": 5,
            "users_at_start": 1,
            "users_at_end": 1,
            "created": "2015-10-03T195620"
        }
        for module_id, module_block in course_fixture.course_structure()['blocks'].items()
        if module_block['type'] == 'video' and module_id not in excluded_module_ids
    ]


def get_mock_course_summaries(course_ids, exclude=None):
    """
    Returns mock course summary api data.

    Arguments
        course_ids -- IDs of courses to return mock data for
        exclude    -- Array of fields to exclude.
    """
    mock_course_summaries = []
    for course_id in course_ids:
        mock_course_summaries.append({
            "created": "2017-02-21T182754",
            "course_id": course_id,
            "catalog_course_title": "Demo Course",
            "catalog_course": "Demo_Course",
            "start_date": "2017-01-10T182754",
            "end_date": "2017-05-02T182754",
            "pacing_type": "self_paced",
            "availability": "Upcoming",
            "count": 1590,
            "cumulative_count": 1835,
            "count_change_7_days": 41,
            "passing_users": 606,
            "enrollment_modes": {
                "audit": {
                    "count": 238,
                    "cumulative_count": 326,
                    "count_change_7_days": -2,
                    "passing_users": 1,
                },
                "credit": {
                    "count": 238,
                    "cumulative_count": 288,
                    "count_change_7_days": 2,
                    "passing_users": 200,
                },
                "verified": {
                    "count": 557,
                    "cumulative_count": 610,
                    "count_change_7_days": 35,
                    "passing_users": 300,
                },
                "professional": {
                    "count": 159,
                    "cumulative_count": 162,
                    "count_change_7_days": 34,
                    "passing_users": 100,
                },
                "honor": {
                    "count": 398,
                    "cumulative_count": 449,
                    "count_change_7_days": -28,
                    "passing_users": 5,
                }
            }
        })

    if exclude:
        # remove all the excluded fields (e.g. passing_users) from the mocked api response
        for field in exclude:
            for summary in mock_course_summaries:
                summary.pop(field, None)
                for mode in summary['enrollment_modes']:
                    summary['enrollment_modes'][mode].pop(field, None)

    return mock_course_summaries


def get_mock_course_summaries_csv(course_ids, has_programs=False, has_passing=False):
    modes = ['audit', 'credit', 'honor', 'professional', 'verified']
    mode_count_fields = ['count', 'cumulative_count']
    if has_passing:
        mode_count_fields.append('passing_users')
    header = (
        'availability,catalog_course,catalog_course_title,count,count_change_7_days,course_id,' +
        'cumulative_count,end_date,' +
        '{enrollment_modes}'
        'pacing_type,{passing_field}{program_fields}start_date'
    ).format(
        # e.g. enrollment_modes.audit.count,enrollment_modes.audit.cumulative_count
        enrollment_modes=','.join(
            ','.join('enrollment_modes.' + mode + '.' + field
                     for field in mode_count_fields)
            for mode in modes) + ',',
        passing_field='passing_users,' if has_passing else '',
        program_fields='program_ids,program_titles,' if has_programs else '',
    )
    rows = [header]

    programs = get_mock_programs()

    # pre-populated course data with arguments for course ID and program data (optional)
    row_template = (
        'Upcoming,Demo_Course,Demo Course,1590,41,{course_id},1835,2017-05-02T182754,' +
        '238,326,{passing_audit}' +
        '238,288,{passing_credit}' +
        '398,449,{passing_honor}' +
        '159,162,{passing_professional}' +
        '557,610,{passing_verified}' +
        'self_paced,{passing_users}{program_data}2017-01-10T182754'
    )

    passing_users = ''
    passing_audit = ''
    passing_credit = ''
    passing_honor = ''
    passing_professional = ''
    passing_verified = ''

    if has_passing:
        passing_users = '606,'
        passing_audit = '1,'
        passing_credit = '200,'
        passing_honor = '5,'
        passing_professional = '100,'
        passing_verified = '300,'

    for course_id in course_ids:
        program_data = ''
        if has_programs:
            associated_programs = [program for program in programs if course_id in set(program['course_ids'])]

            first_program = ''
            second_program = ''
            if len(associated_programs) > 1:
                first_program = associated_programs[0]
                second_program = associated_programs[1]
            elif associated_programs:
                first_program = associated_programs[0]
            for program_field in ['program_id', 'program_title']:
                program_data = program_data + '{}{}{}'.format(
                    first_program[program_field], ' | ' if second_program else '', second_program[program_field]
                ) + ','

        rows.append(row_template.format(
            course_id=course_id,
            passing_users=passing_users,
            passing_audit=passing_audit,
            passing_credit=passing_credit,
            passing_honor=passing_honor,
            passing_professional=passing_professional,
            passing_verified=passing_verified,
            program_data=program_data,
        ))

    row_end = '\r\n'
    return row_end.join(rows) + row_end if len(rows) > 1 else ''


def get_mock_programs():
    return [{
        'program_title': 'Demo Program',
        'program_type': 'Demo',
        'course_ids': [CourseSamples.DEMO_COURSE_ID],
        'program_id': ProgramSamples.DEMO_PROGRAM_ID,
        'created': CREATED_DATETIME_STRING,
    }, {
        'program_title': 'Demo Program2',
        'program_type': 'Demo',
        'course_ids': [CourseSamples.DEPRECATED_DEMO_COURSE_ID],
        'program_id': ProgramSamples.DEMO_PROGRAM2_ID,
        'created': CREATED_DATETIME_STRING,
    }, {
        'program_title': 'Demo Program3',
        'program_type': 'Demo',
        'course_ids': [],
        'program_id': ProgramSamples.DEMO_PROGRAM3_ID,
        'created': CREATED_DATETIME_STRING,
    }, {
        'program_title': 'Demo Program4',
        'program_type': 'Demo',
        'course_ids': [CourseSamples.DEMO_COURSE_ID, CourseSamples.DEPRECATED_DEMO_COURSE_ID, 'another/course/id'],
        'program_id': ProgramSamples.DEMO_PROGRAM4_ID,
        'created': CREATED_DATETIME_STRING,
    }]
