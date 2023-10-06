docker exec -t insights_testing bash -c "
    cd /edx/app/insights/edx_analytics_dashboard/ &&
    source /edx/app/insights/venvs/insights/bin/activate &&
    PATH=\$PATH:/edx/app/insights/nodeenvs/insights/bin:/snap/bin &&
    export TOXENV=${TOXENV} &&
    pip install -r requirements/github.txt &&
    make $TARGETS
"
