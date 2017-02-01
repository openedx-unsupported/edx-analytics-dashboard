#!/bin/bash -xe
. /edx/app/insights/venvs/insights/bin/activate
. /edx/app/insights/nodeenvs/insights/bin/activate

cd /edx/app/insights/edx_analytics_dashboard

coverage xml

bash ./scripts/build-stats-to-datadog.sh
