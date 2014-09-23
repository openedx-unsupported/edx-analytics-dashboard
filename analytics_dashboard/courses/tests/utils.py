import StringIO
import csv
import datetime

from analyticsclient.client import Client
import analyticsclient.constants.activity_type as AT

from courses.permissions import set_user_course_permissions


CREATED_DATETIME = datetime.datetime(year=2014, month=2, day=2)
CREATED_DATETIME_STRING = CREATED_DATETIME.strftime(Client.DATETIME_FORMAT)


def get_mock_enrollment_data(course_id):
    data = []
    start_date = datetime.date(year=2014, month=1, day=1)

    for i in range(31):
        date = start_date + datetime.timedelta(days=i)

        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'course_id': course_id,
            'count': i,
            'created': CREATED_DATETIME_STRING
        })

    return data


def get_mock_enrollment_summary():
    return {
        'last_updated': CREATED_DATETIME,
        'current_enrollment': 30,
        'enrollment_change_last_7_days': 7,
    }


def get_mock_enrollment_summary_and_trend(course_id):
    return get_mock_enrollment_summary(), get_mock_enrollment_data(course_id)


def get_mock_api_enrollment_geography_data(course_id):
    data = []
    items = ((u'USA', u'United States', 500), (u'GER', u'Germany', 100), (u'CAN', u'Canada', 300),
             (None, u'UNKNOWN', 100))
    for item in items:
        data.append({'date': '2014-01-01', 'course_id': course_id, 'count': item[2],
                     'country': {'alpha3': item[0], 'name': item[1]}, 'created': CREATED_DATETIME_STRING})

    return data


def get_mock_api_enrollment_geography_data_limited(course_id):
    data = get_mock_api_enrollment_geography_data(course_id)
    return data[0:1]


def get_mock_presenter_enrollment_geography_data():
    data = [
        {'countryCode': 'USA', 'countryName': 'United States', 'count': 500, 'percent': 0.5},
        {'countryCode': 'CAN', 'countryName': 'Canada', 'count': 300, 'percent': 0.3},
        {'countryCode': 'GER', 'countryName': 'Germany', 'count': 100, 'percent': 0.1},
    ]

    summary = {
        'last_updated': CREATED_DATETIME,
        'num_countries': 3,
        'top_countries': data
    }

    return summary, data


def get_mock_presenter_enrollment_geography_data_limited():
    '''
    Returns a smaller set of countries.
    '''
    summary, data = get_mock_presenter_enrollment_geography_data()
    data = data[0:1]
    data[0]['percent'] = 1.0
    summary.update({
        'num_countries': 1,
        'top_countries': data
    })
    return summary, data


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


# pylint: disable=unused-argument
def mock_course_activity(start_date=None, end_date=None):
    return [
        {
            'interval_end': '2014-09-01T000000',
            AT.ANY: 1000,
            AT.ATTEMPTED_PROBLEM: 0,
            AT.PLAYED_VIDEO: 10000,
            AT.POSTED_FORUM: 45,
            'created': CREATED_DATETIME_STRING
        },
        {
            'interval_end': '2014-09-08T000000',
            AT.ANY: 100,
            AT.ATTEMPTED_PROBLEM: 301,
            AT.PLAYED_VIDEO: 1000,
            AT.POSTED_FORUM: 0,
            'created': CREATED_DATETIME_STRING
        },
    ]
