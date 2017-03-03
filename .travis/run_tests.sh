#!/bin/bash -xe
. /edx/app/insights/venvs/insights/bin/activate
. /edx/app/insights/nodeenvs/insights/bin/activate

apt update
apt install -y xvfb language-pack-en firefox # gettext

# Need firefox 46 specifically, later versions don't work with Karma(frontend testing library).
curl -O https://ftp.mozilla.org/pub/firefox/releases/46.0/linux-x86_64/en-US/firefox-46.0.tar.bz2
tar xvf firefox-46.0.tar.bz2
mv -f firefox /opt
mv -f /usr/bin/firefox /usr/bin/firefox_default
ln -s /opt/firefox/firefox /usr/bin/firefox

cd /edx/app/insights/edx_analytics_dashboard
export PATH=$PATH:$PWD/node_modules/.bin

# Make it so bower can run without sudo.
# https://github.com/GeoNode/geonode/pull/1070
echo '{ "allow_root": true }' > /root/.bowerrc

# Output node.js version
node --version
npm --version

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
