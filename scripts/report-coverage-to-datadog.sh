#!/usr/bin/env bash

#
# This script will report various coverage metrics to datadog.
#
#

if [ "$TRAVIS_BRANCH" = "master" ] && [ "$TRAVIS_PULL_REQUEST" = "false" ] && [ -n $DATADOG_API_KEY ]

    echo "Reporting coverage stats to datadog"
    git clone test-metrics https://github.com/wedaly/test-metrics

    cd test-metrics
    virtualenv venv
    source ./venv/bin/activate
    pip install -r requirements.txt

    cat > unit_test_groups.json <<END
    {
        "unit.analytics_dashboard": "analytics_dashboard/*.py",
        "javascript.analytics_dashboard": "*.js"
    }
    END

    cat > acceptance_test_group.json <<END
    {
        "acceptance.analytics_dashboard": "analytics_dashboard/*.py"
    }
    END

    python -m metrics.coverage unit_test_groups.json `find ../build -name "coverage.xml"`
    python -m metrics.coverage acceptance_test_group.json `find ../acceptance_tests/build -name "coverage.xml"`

    deactivate

fi
