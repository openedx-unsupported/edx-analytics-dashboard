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
