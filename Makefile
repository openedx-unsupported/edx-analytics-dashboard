.PHONY: requirements

ROOT = $(shell echo "$$PWD")
COVERAGE_DIR = $(ROOT)/build/coverage
NODE_BIN=./node_modules/.bin
PYTHON_ENV=py38
DJANGO_VERSION=django32

DJANGO_SETTINGS_MODULE ?= "analytics_dashboard.settings.local"

.PHONY: requirements clean docs

requirements: requirements.py requirements.js

requirements.tox:
	pip3 install -q -r requirements/tox.txt

requirements.py:
	pip3 install -q -r requirements/base.txt --exists-action w

requirements.js:
	npm install --unsafe-perm

test.requirements:
	pip3 install -q -r requirements/test.txt --exists-action w

develop: requirements.js
	pip3 install -q -r requirements/local.txt --exists-action w

tox.migrate: requirements.tox
 	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-migrate

migrate:
	python manage.py migrate

clean: requirements.tox
	find . -name '*.pyc' -delete
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-clean

test_python_no_compress: clean
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-tests

coverage: requirements.tox
	export COVERAGE_DIR=$(COVERAGE_DIR) && \
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-coverage

test_compress: static
	# No longer does anything. Kept for legacy support.

test_python: requirements.tox test_compress test_python_no_compress

requirements.a11y:
	./.travis/a11y_reqs.sh

runserver_a11y: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-runserver_a11y > dashboard.log 2>&1 &

accept: runserver_a11y
ifeq ("${DISPLAY_LEARNER_ANALYTICS}", "True")
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-waffle_learner_analytics
endif
ifeq ("${ENABLE_COURSE_LIST_FILTERS}", "True")
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-waffle_course_filters
endif
ifeq ("${ENABLE_COURSE_LIST_PASSING}", "True")
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-waffle_course_passing
endif
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-create_acceptance_test_soapbox_messages
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-accept
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-delete_acceptance_test_soapbox_messages


# local acceptance tests are typically run with by passing in environment variables on the commandline
# e.g. API_SERVER_URL="http://localhost:9001/api/v0" API_AUTH_TOKEN="edx" make accept_local
accept_local:
	./manage.py create_acceptance_test_soapbox_messages
	pytest -v acceptance_tests --ignore=acceptance_tests/course_validation
	./manage.py delete_acceptance_test_soapbox_messages

a11y: requirements.tox
ifeq ("${DISPLAY_LEARNER_ANALYTICS}", "True")
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-waffle_learner_analytics
endif
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-a11y

course_validation:
	python -m acceptance_tests.course_validation.generate_report

run_check_isort: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-check_isort

run_pycodestyle: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-pycodestyle

run_pylint: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-pylint

quality: run_pylint run_pycodestyle

validate_python: test_python quality

#FIXME validate_js: requirements.js
validate_js:
	$(NODE_BIN)/gulp test
	npm run lint -s

validate: validate_python validate_js

demo:
	python manage.py waffle_switch show_engagement_forum_activity off --create
	python manage.py waffle_switch enable_course_api off --create
	python manage.py waffle_switch display_course_name_in_nav off --create

# compiles djangojs and django .po and .mo files
compile_translations: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-compile_translations

# creates the source django & djangojs files
extract_translations: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-extract_translations

dummy_translations: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-dummy_translations

generate_fake_translations: extract_translations dummy_translations compile_translations

pull_translations:
	cd analytics_dashboard && tx pull -af

update_translations: pull_translations generate_fake_translations

# check if translation files are up-to-date
detect_changed_source_translations: requirements.tox
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-detect_changed_translations

# extract, compile, and check if translation files are up-to-date
validate_translations: extract_translations compile_translations detect_changed_source_translations
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-validate_translations

static_no_compress: static
	# No longer does anything. Kept for legacy support.

static: requirements.tox
	$(NODE_BIN)/webpack --config webpack.prod.config.js
	tox -e $(PYTHON_ENV)-$(DJANGO_VERSION)-static

export CUSTOM_COMPILE_COMMAND = make upgrade
upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip3 install -q -r requirements/pip_tools.txt
	pip-compile --upgrade -o requirements/pip_tools.txt requirements/pip_tools.in
	pip-compile --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --upgrade -o requirements/doc.txt requirements/doc.in
	pip-compile --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --upgrade -o requirements/local.txt requirements/local.in
	pip-compile --upgrade -o requirements/optional.txt requirements/optional.in
	pip-compile --upgrade -o requirements/production.txt requirements/production.in
	pip-compile --upgrade -o requirements/tox.txt requirements/tox.in
	pip-compile --upgrade -o requirements/travis.txt requirements/travis.in
	# Let tox control the Django version for tests
	grep -e "^django==" requirements/base.txt > requirements/django.txt
	sed '/^[dD]jango==/d' requirements/test.txt > requirements/test.tmp
	mv requirements/test.tmp requirements/test.txt

docs:
	tox -e docs
