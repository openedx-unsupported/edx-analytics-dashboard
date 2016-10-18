#!/usr/bin/env bash

git clone https://github.com/edx/edx-analytics-data-api.git
cd edx-analytics-data-api
if [ -z $1 ]; then
  git checkout master
else
  git checkout $1
fi
virtualenv venv
source venv/bin/activate
make requirements
make test.install_elasticsearch
deactivate
cd -
