#! /usr/bin/env python

"""
This script generates a report containing the following details for each course:
 * HTTP status codes for every course page in Insights
 * Boolean indicating if the API has activity and enrollment data for the course

A live feed of the report can be tail'ed from <TIMESTAMP>-course_report.log. The final output CSV is available
in the file <TIMESTAMP>-course_report.csv. <TIMESTAMP> is the time, in UTC, at which this script was initialized.

To execute this script run the following command from the parent directory of acceptance_tests:

    $ python -m acceptance_tests.course_validation.generate_report
"""

import csv
import datetime
import logging
import time
from multiprocessing import Queue, Pool

from pyquery import PyQuery as pq
import requests
from analyticsclient.client import Client

from acceptance_tests.course_validation import API_SERVER_URL, API_AUTH_TOKEN, LMS_URL, LMS_USERNAME, LMS_PASSWORD, \
    BASIC_AUTH_CREDENTIALS, DASHBOARD_SERVER_URL
from acceptance_tests.course_validation.course_reporter import CourseReporter, API_REPORT_KEYS, COURSE_PAGES


NUM_PROCESSES = 8
TIMESTAMP = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
logger = logging.getLogger(__name__)


def _setup_logging():
    logger.setLevel(logging.DEBUG)

    # Log all debug and higher to files
    fh = logging.FileHandler('{}-course_report.log'.format(TIMESTAMP))
    fh.setLevel(logging.DEBUG)

    # Log info and higher to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Setup log formatting
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Disable requests debug logs
    logging.getLogger("requests").setLevel(logging.WARNING)


def check_course(course_id):
    """
    Gather info on the given course.
    """
    logger.debug('Checking %s...', course_id)

    course = check_course.api_client.courses(course_id)
    reporter = CourseReporter(course, check_course.cookies)
    report = reporter.report()
    logger.info(report)
    check_course.q.put(report)


def pool_init(q, api_client, cookies):
    """
    Initialize the variables needed by the mapping function.
    """
    check_course.q = q
    check_course.api_client = api_client
    check_course.cookies = cookies


def write_csv(reports):
    """
    Write the data from the Queue to a CSV.
    """
    logger.info('Writing data to CSV...')

    keys = ['course_id'] + COURSE_PAGES + API_REPORT_KEYS
    filename = '{}-course_report.csv'.format(TIMESTAMP)

    f = open(filename, 'wb')
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writer.writerow(keys)

    while not reports.empty():
        dict_writer.writerow(reports.get())

    logger.info('Data was saved to %s.', filename)


def login(http_client):
    logger.info('Logging into LMS...')

    lms_login = '{}/login'.format(LMS_URL)
    lms_login_ajax = '{}/login_ajax'.format(LMS_URL)

    # Make a call to the login page to get cookies (esp. CSRF token)
    http_client.get(lms_login)

    # Set the headers and data for the actual login request.
    headers = {
        'referer': lms_login
    }
    data = {
        'email': LMS_USERNAME,
        'password': LMS_PASSWORD,
        'csrfmiddlewaretoken': http_client.cookies['csrftoken']
    }

    # Login!
    r = http_client.post(lms_login_ajax, data=data, headers=headers)
    success = r.json().get('success', False)

    if not success:
        msg = 'Login failed!'
        logger.error(msg)
        raise Exception(msg)

    logger.info('Login succeeded.')


def get_courses(http_client):
    course_list_url = '{}/courses/'.format(DASHBOARD_SERVER_URL)
    r = http_client.get(course_list_url)

    if r.status_code != 200:
        msg = 'Failed to retrieve course list!'
        logger.error(msg)
        raise Exception(msg)

    d = pq(r.text)
    courses = []
    elements = d('.course-list .course-title')
    for element in elements:
        courses.append(element.text.strip())

    logger.info('Retrieved %s courses from %s.', len(courses), course_list_url)

    return courses


def main():
    start = time.time()
    api_client = Client(base_url=API_SERVER_URL, auth_token=API_AUTH_TOKEN, timeout=1000)
    http_client = requests.Session()

    if BASIC_AUTH_CREDENTIALS:
        http_client.auth = BASIC_AUTH_CREDENTIALS

    login(http_client)

    # Basic auth is no longer needed
    http_client.auth = None

    # Get courses
    courses = get_courses(http_client)

    # Collect the data
    reports = Queue()
    try:
        p = Pool(NUM_PROCESSES, pool_init, [reports, api_client, http_client.cookies])
        p.map(check_course, courses)
    except Exception as e:  # pylint: disable=broad-except
        logger.error('Validation failed to finish: %s', e)

    # Write the data to an external file
    write_csv(reports)
    end = time.time()

    logger.info('Finished in %d seconds.', end - start)


if __name__ == "__main__":
    _setup_logging()
    main()
