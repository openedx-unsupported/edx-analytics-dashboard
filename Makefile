.PHONY: requirements

ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
NODE_BIN=./node_modules/.bin

DJANGO_SETTINGS_MODULE ?= "analytics_dashboard.settings.local"

.PHONY: requirements clean

# pin to 9.0.3 until tox-battery upgrades
pin_pip:
	pip install --upgrade pip==9.0.3

requirements: requirements.py requirements.js

requirements.py:
	pip install -q -r requirements/base.txt --exists-action w

requirements.js:
	npm install --unsafe-perm

test.requirements:
	pip install -q -r requirements/test.txt --exists-action w

develop: requirements.js
	pip install -q -r requirements/local.txt --exists-action w

migrate:
	python manage.py migrate --run-syncdb

clean:
	find . -name '*.pyc' -delete
	coverage erase

test_python_no_compress: clean
	pytest analytics_dashboard common --cov=analytics_dashboard --cov=common --cov-branch --cov-report=html:$(COVERAGE)/html/ \
	--cov-report=xml:$(COVERAGE)/coverage.xml

test_compress: static
	# No longer does anything. Kept for legacy support.

test_python: test_compress test_python_no_compress

accept:
ifeq ("${DISPLAY_LEARNER_ANALYTICS}", "True")
	./manage.py waffle_flag enable_learner_analytics --create --everyone
endif
ifeq ("${ENABLE_COURSE_LIST_FILTERS}", "True")
	./manage.py waffle_switch enable_course_filters on --create
endif
ifeq ("${ENABLE_COURSE_LIST_PASSING}", "True")
	./manage.py waffle_switch enable_course_passing on --create
endif
	./manage.py create_acceptance_test_soapbox_messages
	pytest -v acceptance_tests -k 'not NUM_PROCESSES=1' --ignore=acceptance_tests/course_validation
	./manage.py delete_acceptance_test_soapbox_messages

# local acceptance tests are typically run with by passing in environment variables on the commandline
# e.g. API_SERVER_URL="http://localhost:9001/api/v0" API_AUTH_TOKEN="edx" make accept_local
accept_local:
	./manage.py create_acceptance_test_soapbox_messages
	pytest -v acceptance_tests --ignore=acceptance_tests/course_validation
	./manage.py delete_acceptance_test_soapbox_messages

a11y:
ifeq ("${DISPLAY_LEARNER_ANALYTICS}", "True")
	./manage.py waffle_flag enable_learner_analytics --create --everyone
endif
	BOKCHOY_A11Y_CUSTOM_RULES_FILE=./node_modules/edx-custom-a11y-rules/lib/custom_a11y_rules.js SELENIUM_BROWSER=firefox pytest -v a11y_tests -k 'not NUM_PROCESSES=1' --ignore=acceptance_tests/course_validation

course_validation:
	python -m acceptance_tests.course_validation.generate_report

quality:
	pep8 acceptance_tests analytics_dashboard common
	PYTHONPATH=".:./analytics_dashboard:$PYTHONPATH" pylint --rcfile=pylintrc acceptance_tests analytics_dashboard common

validate_python: test.requirements test_python quality

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
compile_translations:
	python manage.py compilemessages

# creates the source django & djangojs files
extract_translations:
	cd analytics_dashboard && python ../manage.py makemessages -l en -v1 --ignore="docs/*" --ignore="src/*" --ignore="i18n/*" --ignore="assets/*" --ignore="static/bundles/*" -d django
	cd analytics_dashboard && python ../manage.py makemessages -l en -v1 --ignore="docs/*" --ignore="src/*" --ignore="i18n/*" --ignore="assets/*" --ignore="static/bundles/*" -d djangojs

dummy_translations:
	cd analytics_dashboard && i18n_tool dummy -v

generate_fake_translations: extract_translations dummy_translations compile_translations

pull_translations:
	cd analytics_dashboard && tx pull -af

update_translations: pull_translations generate_fake_translations

# check if translation files are up-to-date
detect_changed_source_translations:
	cd analytics_dashboard && i18n_tool changed

# extract, compile, and check if translation files are up-to-date
validate_translations: extract_translations compile_translations detect_changed_source_translations
	cd analytics_dashboard && i18n_tool validate

static_no_compress: static
	# No longer does anything. Kept for legacy support.

static:
	$(NODE_BIN)/webpack --config webpack.prod.config.js
	# collectstatic creates way too much output with the cldr-data directory output so silence that directory
	echo "Running collectstatic while silencing cldr-data/main/* ..."
	python manage.py collectstatic --noinput | sed -n '/.*node_modules\/cldr-data\/main\/.*/!p'

export CUSTOM_COMPILE_COMMAND = make upgrade
upgrade: ## update the requirements/*.txt files with the latest packages satisfying requirements/*.in
	pip install -q -r requirements/pip_tools.txt
	pip-compile --upgrade -o requirements/pip_tools.txt requirements/pip_tools.in
	pip-compile --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --upgrade -o requirements/doc.txt requirements/doc.in
	pip-compile --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --upgrade -o requirements/local.txt requirements/local.in
	pip-compile --upgrade -o requirements/optional.txt requirements/optional.in
	pip-compile --upgrade -o requirements/production.txt requirements/production.in

