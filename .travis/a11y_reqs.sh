#!/bin/bash -xe

apt update
apt install -y xvfb language-pack-en firefox

# Need firefox 46 specifically, later versions don't work with Karma(frontend testing library).
curl -O https://ftp.mozilla.org/pub/firefox/releases/46.0/linux-x86_64/en-US/firefox-46.0.tar.bz2
tar xvf firefox-46.0.tar.bz2
mv -f firefox /opt
mv -f /usr/bin/firefox /usr/bin/firefox_default
ln -s /opt/firefox/firefox /usr/bin/firefox
