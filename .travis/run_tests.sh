#!/bin/bash -xe
. /edx/app/insights/venvs/insights/bin/activate
. /edx/app/insights/nodeenvs/insights/bin/activate


cd /edx/app/insights/edx_analytics_dashboard
export PATH=$PATH:$PWD/node_modules/.bin

# Output node.js version
node --version
npm --version

# HACK: remove package-lock.json because otherwise npm doesn't want to git clone (I WISH I KNEW WHY)
rm package-lock.json

# Pin pip version
make pin_pip

make develop
make migrate

# Compile assets and run validation
make static_no_compress
make validate_translations
make validate
make generate_fake_translations

# The following tests need insights running. We have to do it here
# because we need to wait till all the requirements have been installed
# otherwise the server will startup with potentially the wrong libraries.
/edx/bin/python.insights /edx/bin/manage.insights runserver 0.0.0.0:9000 --noreload --traceback > dashboard.log 2>&1 &
xvfb-run make accept
xvfb-run make a11y
