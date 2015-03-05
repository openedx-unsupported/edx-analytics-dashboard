#! /usr/bin/env python

"""
This script executes reporters that provide data about course pages. Any reporter inheriting from ReporterBase
can be used.

All collected data is logged to a local file and indexed in an Elasticsearch index. The local file can be found at
<TIMESTAMP>-course_report.log. <TIMESTAMP> is the time, in UTC, at which this script was initialized.

Elasticsearch data is written to the index named course_reports. Note that subsequent runs of this script will overwrite
existing data as new data is collected.

The list of courses on which to report is pulled from the course structure API and saved locally in a file named
courses.json. Subsequent script runs will use this file instead of the API. If you want fresh data,
simply delete the file.

To execute this script run the following command from the parent directory of acceptance_tests:

    $ python -m acceptance_tests.course_validation.report_runner
"""

import datetime
import io
import json
import logging
from multiprocessing import Pool
from os.path import abspath, dirname, join
import time
import traceback

from elasticsearch import Elasticsearch
import requests

from acceptance_tests.course_validation import LMS_URL, LMS_USERNAME, LMS_PASSWORD, \
    BASIC_AUTH_CREDENTIALS, COURSE_API_URL, COURSE_API_KEY, ENABLE_AUTO_AUTH, DASHBOARD_SERVER_URL
from acceptance_tests.course_validation.report_generators import CoursePerformanceReportGenerator
from common.clients import CourseStructureApiClient


NUM_PROCESSES = 8
TIMESTAMP = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')

logger = logging.getLogger(__name__)
es = Elasticsearch(retry_on_timeout=True)
index_name = 'course_reports'

# Add additional reports here to get different information.
# For example, if you want screenshots, add the CoursePerformanceScreenshotReporter.
# Obvious Note: The more reporters you run, the longer the script will run.
reporters = [CoursePerformanceReportGenerator, ]


def _setup_logging():
    level = logging.DEBUG
    msg_format = '%(asctime)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        filename='{}-course_report.log'.format(TIMESTAMP),
        format=msg_format,
        level=level)

    # Log to console, in addition to file
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(logging.Formatter(msg_format))
    logging.root.addHandler(ch)

    # Disable requests and elasticsearch debug logs
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('elasticsearch').setLevel(logging.WARNING)
    logging.getLogger('elasticsearch.trace').setLevel(logging.WARNING)


def check_course(course_id):
    """
    Gather info on the given course.
    """
    logger.debug('Checking %s...', course_id)

    valid = True

    for reporter_class in reporters:
        try:
            # Generate a report for each reporter
            reporter = reporter_class(course_id, check_course.cookies)
            _valid, report = reporter.generate_report()
            valid &= _valid
        except Exception as e:  # pylint: disable=broad-except
            logger.error('Validation for course %s failed: %s\n%s', course_id, e, traceback.format_exc())
            valid = False
            report = {'course_id': course_id, 'course_valid': False, 'error': unicode(e)}

        # Dump the info to the log and Elasticsearch
        logger.info(json.dumps(report))
        try:
            doc_type = reporter_class.REPORT_NAME
            es.index(index=index_name, doc_type=doc_type, body=report, id=course_id)
        except Exception as e:
            logger.error('%s\n%s', e, traceback.format_exc())
            raise

        if valid:
            logger.info('Successfully validated %s.', course_id)
        else:
            logger.error('Course %s is not valid!', course_id)


def pool_init(cookies):
    """
    Initialize the variables needed by the mapping function.
    """
    check_course.cookies = cookies


def login(http_client):
    failure_msg = 'Login failed!'

    if ENABLE_AUTO_AUTH:
        logger.info('Logging into dashboard with auto auth...')
        response = http_client.get('{}/test/auto_auth/'.format(DASHBOARD_SERVER_URL))

        if response.status_code == 200:
            logger.info('Login succeeded.')
            return
        else:
            logger.fatal(failure_msg)
            raise Exception(failure_msg)

    logger.info('Logging into LMS...')

    if BASIC_AUTH_CREDENTIALS:
        http_client.auth = BASIC_AUTH_CREDENTIALS

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
        msg = failure_msg
        logger.error(msg)
        raise Exception(msg)

    # Basic auth is no longer needed
    http_client.auth = None

    logger.info('Login succeeded.')


def get_courses():
    filename = 'courses.json'

    try:
        with io.open(filename, 'r', encoding='utf-8') as f:
            courses = json.load(f)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning('Failed to read courses from file: %s', e)
        courses = []

    if not courses:
        logger.info('Retrieving courses from API...')
        client = CourseStructureApiClient(COURSE_API_URL, COURSE_API_KEY)
        courses = client.all_courses
        courses = [course['id'] for course in courses]
        courses.sort(key=lambda course: course.lower())

        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(courses, ensure_ascii=False)))

    logger.info('Retrieved %s courses.', len(courses))

    return courses


def main():
    start = time.time()
    http_client = requests.Session()

    # Log into Insights using either OIDC (via LMS) or auto auth.
    login(http_client)

    # Get courses on which to report
    courses = get_courses()

    # Create index to store results
    if not es.indices.exists(index_name):
        es.indices.create(index_name)

        # Create the mappings
        mappings_file = join(dirname(abspath(__file__)), 'mappings.json')
        with io.open(mappings_file, 'r', encoding='utf-8') as f:
            mappings = json.load(f)

        for doc_type, body in mappings.iteritems():
            es.indices.put_mapping(index=index_name, doc_type=doc_type, body=body)

    def finish():
        end = time.time()
        logger.info('Finished in %d seconds.', end - start)

    try:
        p = Pool(NUM_PROCESSES, pool_init, [http_client.cookies])
        p.map(check_course, courses)
        p.close()
    except (KeyboardInterrupt, SystemExit):
        p.terminate()
        finish()
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error('Validation failed to finish: %s', e)

    finish()


if __name__ == "__main__":
    _setup_logging()
    main()
