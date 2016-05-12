#!/usr/bin/env bash

git clone https://github.com/edx/edx-analytics-data-api.git
cd edx-analytics-data-api
virtualenv venv
source venv/bin/activate
make requirements
make test.install_elasticsearch
deactivate
cd -
