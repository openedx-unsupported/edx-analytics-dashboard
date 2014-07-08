#!/bin/sh

echo "Starting server..."

# --noreload is only runs one processes (which we can then kill)
./manage.py runserver --noreload &

# save the process to kill later
PID=$!

echo "Running acceptance tests..."
./manage.py test courses/test/acceptance/tests/

echo "Shutting down server..."
kill -9 $PID