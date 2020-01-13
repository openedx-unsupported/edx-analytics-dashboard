#!/bin/bash -xe

# Can be used to update a devstack container.  This is not the right permanent home for
# this script, but it is a start.
# Note: Copied and modified from .travis/run_tests.sh

. /edx/app/insights/venvs/insights/bin/activate
. /edx/app/insights/nodeenvs/insights/bin/activate

cd /edx/app/insights/edx_analytics_dashboard
export PATH=$PATH:$PWD/node_modules/.bin

# Output node.js version
node --version
npm --version

# HACK: remove package-lock.json because otherwise npm doesn't want to git clone (I WISH I KNEW WHY)
# Note: Copied from .travis/run_tests.sh
rm package-lock.json

# Pin pip version
make pin_pip

make develop
make migrate
make static
