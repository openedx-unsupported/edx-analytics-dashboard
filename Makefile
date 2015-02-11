.PHONY: requirements

ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
PACKAGES = analytics_dashboard courses django_rjs help
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
	cd analytics_dashboard && ./manage.py migrate

clean:
	find . -name '*.pyc' -delete
	coverage erase

test_python: clean
	cd analytics_dashboard && ./manage.py test --settings=analytics_dashboard.settings.test --with-ignore-docstrings \
		--exclude-dir=analytics_dashboard/settings --exclude-dir=analytics_dashboard/migrations --with-coverage \
		--cover-inclusive --cover-branches --cover-html --cover-html-dir=$(COVERAGE)/html/ \
		--cover-xml --cover-xml-file=$(COVERAGE)/coverage.xml \
		$(foreach package,$(PACKAGES),--cover-package=$(package)) \
		$(PACKAGES)

accept:
	nosetests -v acceptance_tests --processes=$(NUM_PROCESSES) --process-timeout=120 --exclude-dir=acceptance_tests/course_validation

course_validation:
	python -m acceptance_tests.course_validation.generate_report

quality:
	pep8 analytics_dashboard
	cd analytics_dashboard && pylint --rcfile=../pylintrc $(PACKAGES)

	# Ignore module level docstrings and all test files
	#cd analytics_dashboard && pep257 --ignore=D100,D203 --match='(?!test).*py' $(PACKAGES)

validate_python: test.requirements test_python quality

validate_js: requirements.js
	$(NODE_BIN)/gulp test
	$(NODE_BIN)/gulp lint
	$(NODE_BIN)/gulp jscs

validate: validate_python validate_js

demo:
	cd analytics_dashboard && ./manage.py switch show_engagement_forum_activity on --create
	cd analytics_dashboard && ./manage.py switch display_verified_enrollment on --create

compile_translations:
	cd analytics_dashboard && i18n_tool generate -v

extract_translations:
	cd analytics_dashboard && DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} PYTHONPATH=".:$PYTHONPATH" i18n_tool extract -v

dummy_translations:
	cd analytics_dashboard && i18n_tool dummy -v

generate_fake_translations: extract_translations dummy_translations compile_translations

pull_translations:
	cd analytics_dashboard && tx pull -a

update_translations: pull_translations generate_fake_translations

static:
	$(NODE_BIN)/r.js -o build.js
	cd analytics_dashboard && ./manage.py collectstatic --noinput
	cd analytics_dashboard && ./manage.py compress
