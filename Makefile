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

test_compress: static_no_compress
	python manage.py compress --settings=analytics_dashboard.settings.test

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
	nosetests -v acceptance_tests -e NUM_PROCESSES=1 --exclude-dir=acceptance_tests/course_validation
	./manage.py delete_acceptance_test_soapbox_messages

# local acceptance tests are typically run with by passing in environment variables on the commandline
# e.g. API_SERVER_URL="http://localhost:9001/api/v0" API_AUTH_TOKEN="edx" make accept_local
accept_local:
	./manage.py create_acceptance_test_soapbox_messages
	nosetests -v acceptance_tests --exclude-dir=acceptance_tests/course_validation
	./manage.py delete_acceptance_test_soapbox_messages

a11y:
ifeq ("${DISPLAY_LEARNER_ANALYTICS}", "True")
	./manage.py waffle_flag enable_learner_analytics --create --everyone
endif
	BOKCHOY_A11Y_CUSTOM_RULES_FILE=./node_modules/edx-custom-a11y-rules/lib/custom_a11y_rules.js SELENIUM_BROWSER=firefox nosetests -v a11y_tests -e NUM_PROCESSES=1 --exclude-dir=acceptance_tests/course_validation

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
	python manage.py waffle_switch display_course_name_in_nav off --create

# compiles djangojs and django .po and .mo files
compile_translations:
	python manage.py compilemessages

# creates the source django & djangojs files
extract_translations:
	cd analytics_dashboard && python ../manage.py makemessages -l en -v1 --ignore="docs/*" --ignore="src/*" --ignore="i18n/*" --ignore="assets/*" -d django
	cd analytics_dashboard && python ../manage.py makemessages -l en -v1 --ignore="docs/*" --ignore="src/*" --ignore="i18n/*" --ignore="assets/*" -d djangojs

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

static_no_compress:
	$(NODE_BIN)/r.js -o build.js
	# collectstatic creates way too much output so silence it with verbosity=0
	python manage.py collectstatic --noinput -v 0

static: static_no_compress
	python manage.py compress
