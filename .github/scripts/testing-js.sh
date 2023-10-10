export NODE_VERSION=18.15.0

docker exec -t insights_testing bash -c "
    cd /edx/app/insights/edx_analytics_dashboard/ &&
    source /edx/app/insights/venvs/insights/bin/activate &&
    PATH=\$PATH:/edx/app/insights/nodeenvs/insights/bin:/snap/bin &&
    export TOXENV=${TOXENV} &&
    pip install -r requirements/github.txt &&
    set -x &&
    nodeenv --node=${NODE_VERSION} /edx/app/insights/nodeenvs/insights-test-${NODE} &&
    source /edx/app/insights/nodeenvs/insights-test-${NODE}/bin/activate &&
    node --version && npm --version
    make $TARGETS
"
