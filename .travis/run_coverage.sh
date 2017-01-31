#!/bin/bash -xe
. /edx/app/insights/venvs/insights/bin/activate
. /edx/app/insights/nodeenvs/insights/bin/activate

coverage xml

bash ./scripts/build-stats-to-datadog.sh
