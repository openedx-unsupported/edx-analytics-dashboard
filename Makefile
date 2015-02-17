.PHONY: requirements

ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
NUM_PROCESSES = 2
NODE_BIN=./node_modules/.bin

DJANGO_SETTINGS_MODULE := "analytics_dashboard.settings.local"

.PHONY: requirements clean

requirements: requirements.js
	pip install -q -r requirements/base.txt --exists-action w

requirements.js:
	npm install
	$(NODE_BIN)/bower install

test.requirements: requirements
	pip install -q -r requirements/test.txt --exists-action w

develop: test.requirements
	pip install -q -r requirements/local.txt --exists-action w

test.acceptance: develop
	git clone https://github.com/edx/edx-analytics-data-api.git
	pip install -q -r edx-analytics-data-api/requirements/base.txt

migrate:
	python manage.py migrate

clean:
	find . -name '*.pyc' -delete
	coverage erase

test_python: clean
	python manage.py test analytics_dashboard --settings=analytics_dashboard.settings.test --with-coverage \
	--cover-package=analytics_dashboard --exclude-dir=analytics_dashboard/settings --exclude-dir=analytics_dashboard/migrations \
		--cover-branches --cover-html --cover-html-dir=$(COVERAGE)/html/ --with-ignore-docstrings \
		--cover-xml --cover-xml-file=$(COVERAGE)/coverage.xml --exclude=core/admin

accept:
	nosetests -v acceptance_tests --processes=$(NUM_PROCESSES) --process-timeout=120 --exclude-dir=acceptance_tests/course_validation

course_validation:
	python -m acceptance_tests.course_validation.generate_report

quality:
	pep8 acceptance_tests analytics_dashboard
	PYTHONPATH=".:./analytics_dashboard:$PYTHONPATH" pylint --rcfile=pylintrc acceptance_tests analytics_dashboard

validate_python: test.requirements test_python quality

validate_js: requirements.js
	$(NODE_BIN)/gulp test
	$(NODE_BIN)/gulp lint
	$(NODE_BIN)/gulp jscs

validate: validate_python validate_js

demo:
	python manage.py switch show_engagement_forum_activity on --create
	python manage.py switch display_verified_enrollment on --create

compile_translations:
	cd analytics_dashboard && i18n_tool generate -v

extract_translations:
	cd analytics_dashboard && i18n_tool extract -v

dummy_translations:
	cd analytics_dashboard && i18n_tool dummy -v

generate_fake_translations: extract_translations dummy_translations compile_translations

pull_translations:
	cd analytics_dashboard && tx pull -a

update_translations: pull_translations generate_fake_translations

static:
	$(NODE_BIN)/r.js -o build.js
	python manage.py collectstatic --noinput
	python manage.py compress
