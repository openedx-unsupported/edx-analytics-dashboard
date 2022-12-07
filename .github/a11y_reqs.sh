#!/bin/bash -xe

apt update
apt install -y  language-pack-en firefox

INSTALL_DIR="/usr/local/bin"
url="https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz"

curl -s -L "$url" | tar -xz
chmod +x geckodriver

mv geckodriver "$INSTALL_DIR"
