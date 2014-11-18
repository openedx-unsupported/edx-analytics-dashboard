#!/usr/bin/env bash

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
export ENABLE_AUTH_TESTS=False
export ENABLE_ERROR_PAGE_TESTS=False

echo "Migrating Analytics Dashboard DB..."
make migrate

echo "Preparing Analytics Data API..."
cd edx-analytics-data-api/
make travis
cd -

echo "Starting Analytics Data API Server..."
./edx-analytics-data-api/manage.py runserver 9001 --noreload &

echo "Starting Analytics Dashboard Server..."
./analytics_dashboard/manage.py runserver 9000 --noreload &

echo "Running acceptance tests..."
make accept -e NUM_PROCESSES=1

# capture the exit code from the test.  Anything more than 0 indicates failed cases.
EXIT_CODE=$?

echo "Shutting down server..."
stopServers

if [[ "$EXIT_CODE" = "0" ]]; then
    echo "All tests passed..."
else
    echo "Failed tests..."
fi
exit $EXIT_CODE
