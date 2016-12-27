.PHONY: requirements

ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
NODE_BIN=./node_modules/.bin

DJANGO_SETTINGS_MODULE ?= "analytics_dashboard.settings.local"

.PHONY: requirements clean

requirements: requirements.py requirements.js

requirements.py:
	pip install -q -r requirements/base.txt --exists-action w

requirements.js:
	npm install
	$(NODE_BIN)/bower install

test.requirements: requirements
	pip install -q -r requirements/test.txt --exists-action w

develop: test.requirements
	pip install -q -r requirements/local.txt --exists-action w

migrate:
	python manage.py migrate --run-syncdb

clean:
	find . -name '*.pyc' -delete
	coverage erase

test_python_no_compress: clean
	python manage.py test analytics_dashboard common --settings=analytics_dashboard.settings.test --with-coverage \
	--cover-package=analytics_dashboard --cover-package=common --cover-branches --cover-html --cover-html-dir=$(COVERAGE)/html/ \
	--with-ignore-docstrings --cover-xml --cover-xml-file=$(COVERAGE)/coverage.xml

test_compress:
	python manage.py compress --settings=analytics_dashboard.settings.test

test_python: test_compress test_python_no_compress

accept:
	./scripts/runTests.sh acceptance_tests

# local acceptance tests are typically run with by passing in environment variables on the commandline
# e.g. API_SERVER_URL="http://localhost:9001/api/v0" API_AUTH_TOKEN="edx" make accept_local
accept_local:
	nosetests -v acceptance_tests --exclude-dir=acceptance_tests/course_validation

a11y:
	BOKCHOY_A11Y_CUSTOM_RULES_FILE=./node_modules/edx-custom-a11y-rules/lib/custom_a11y_rules.js SELENIUM_BROWSER=phantomjs ./scripts/runTests.sh a11y_tests

course_validation:
	python -m acceptance_tests.course_validation.generate_report

quality:
	pep8 acceptance_tests analytics_dashboard common
	PYTHONPATH=".:./analytics_dashboard:$PYTHONPATH" pylint --rcfile=pylintrc acceptance_tests analytics_dashboard common

validate_python: test.requirements test_python quality

#FIXME validate_js: requirements.js
validate_js:
	$(NODE_BIN)/gulp test
	$(NODE_BIN)/gulp lint

validate: validate_python validate_js

demo:
	python manage.py waffle_switch show_engagement_forum_activity off --create
	python manage.py waffle_switch enable_course_api off --create
	python manage.py waffle_switch display_names_for_course_index off --create
	python manage.py waffle_switch display_course_name_in_nav off --create

# compiles the *.po & *.mo files
compile_translations:
	cd analytics_dashboard && i18n_tool generate -v

# creates the django-partial.po & django-partial.mo files
extract_translations:
	cd analytics_dashboard && i18n_tool extract -v

dummy_translations:
	cd analytics_dashboard && i18n_tool dummy -v

generate_fake_translations: extract_translations dummy_translations compile_translations

pull_translations:
	cd analytics_dashboard && tx pull -a

update_translations: pull_translations generate_fake_translations

# check if translation files are up-to-date
detect_changed_source_translations:
	cd analytics_dashboard && i18n_tool changed

# extract, compile, and check if translation files are up-to-date
validate_translations: extract_translations compile_translations detect_changed_source_translations

static_no_compress:
	$(NODE_BIN)/r.js -o build.js
	# collectstatic creates way too much output with the cldr-data directory output so silence that directory
	echo "Running collectstatic while silencing cldr-data/main/* ..."
	python manage.py collectstatic --noinput | sed -n '/.*bower_components\/cldr-data\/main\/.*/!p'

static: static_no_compress
	python manage.py compress
