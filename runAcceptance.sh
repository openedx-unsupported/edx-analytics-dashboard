#!/usr/bin/env bash

# this is the command that runs our server
# --noreload is only runs one processes (which we can then kill)
RUN_SERVER_SUBCMD="./manage.py runserver --noreload"
RUN_SERVER_CMD="cd analytics_dashboard && ${RUN_SERVER_SUBCMD}"

# this stops the django servers
function stopServers {
    kill $(ps aux | grep "[p]ython $RUN_SERVER_SUBCMD" | awk '{print $2}')
}

echo "Stop any running servers..."
stopServers

echo "Starting server..."
eval "$RUN_SERVER_CMD &"

echo "Running acceptance tests..."
cd acceptance_tests && nosetests

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
