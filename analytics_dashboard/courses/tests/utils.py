import StringIO
import csv
import datetime


def get_mock_enrollment_data(course_id):
    data = []
    start_date = datetime.date(year=2014, month=1, day=1)

    for i in range(31):
        date = start_date + datetime.timedelta(days=i)

        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'course_id': course_id,
            'count': i
        })

    return data


def get_mock_enrollment_summary():
    return {
        'date': datetime.date(year=2014, month=1, day=31),
        'current_enrollment': 30,
        'enrollment_change_last_1_days': 1,
        'enrollment_change_last_7_days': 7,
        'enrollment_change_last_30_days': 30,
    }


def get_mock_enrollment_location_data(course_id):
    data = []
    for item in (
    (u'USA', u'United States', 500), (u'GER', u'Germany', 100), (u'CAN', u'Canada', 300)):
        data.append({'date': '2014-01-01', 'course_id': course_id, 'count': item[2],
                     'country': {'alpha3': item[0], 'name': item[1]}})
    return data


def convert_list_of_dicts_to_csv(data, fieldnames=None):
    output = StringIO.StringIO()
    fieldnames = fieldnames or sorted(data[0].keys())

    writer = csv.DictWriter(output, fieldnames)
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()
