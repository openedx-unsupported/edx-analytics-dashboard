#!/usr/bin/env bash

TEST_DIR=${1?arg missing, specify a directory to find tests}

# this stops the django servers
stopServers() {
    kill $(ps aux | grep "[m]anage.py" | awk '{print $2}')
}

echo "Stop any already running servers..."
stopServers

echo "Setting test related environment variables..."
export API_SERVER_URL=http://127.0.0.1:9001/api/v0
export API_AUTH_TOKEN=edx
export LMS_HOSTNAME=lms
export LMS_PASSWORD=pass
export LMS_USERNAME=user
export ENABLE_AUTO_AUTH=True
export ENABLE_OAUTH_TESTS=False
export ENABLE_ERROR_PAGE_TESTS=False
export DISPLAY_LEARNER_ANALYTICS=True

# echo "Migrating Analytics Dashboard DB..."
# make migrate

echo "Preparing Analytics Data API..."
cd edx-analytics-data-api/
source venv/bin/activate
DJANGO_SETTINGS_MODULE="analyticsdataserver.settings.local" make develop
DJANGO_SETTINGS_MODULE="analyticsdataserver.settings.local" make travis
deactivate
cd -
mkdir -p logs

echo "Enabling waffle flags..."
if [[ "${DISPLAY_LEARNER_ANALYTICS}" = "True" ]]; then
    ./manage.py waffle_flag enable_learner_analytics on --create --everyone
fi

echo "Starting Analytics Data API Server..."
./scripts/run_analytics_data_api.sh

echo "Starting Analytics Dashboard Server..."
./manage.py runserver 9000 --noreload --traceback > logs/dashboard.log 2>&1 &

echo "Running $TEST_DIR tests..."
nosetests -v $TEST_DIR -e NUM_PROCESSES=1 --exclude-dir=acceptance_tests/course_validation

# capture the exit code from the test.  Anything more than 0 indicates failed cases.
EXIT_CODE=$?

echo "Shutting down server..."
stopServers

if [[ "$EXIT_CODE" = "0" ]]; then
    echo "All tests passed..."
else
    echo "Failed tests..."
    echo -e "\033[33;34m Server Logs for Analytics Data API Server... \033[0m "
    cat logs/api.log
    echo -e "\033[33;34m Server logs for Analytics Dashboard Server... \033[0m "
    cat logs/dashboard.log
fi
exit $EXIT_CODE
