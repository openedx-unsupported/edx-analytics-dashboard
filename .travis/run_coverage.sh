#!/bin/bash -xe

cd /edx/app/insights/edx_analytics_dashboard

make coverage

bash ./scripts/build-stats-to-datadog.sh
