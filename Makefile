ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
PACKAGES = analytics_dashboard courses
NUM_PROCESSES = 2

requirements:
	pip install -q -r requirements/base.txt --exists-action w

test.requirements: requirements
	pip install -q -r requirements/test.txt --exists-action w

develop: test.requirements
	pip install -q -r requirements/local.txt --exists-action w

syncdb:
	cd analytics_dashboard && ./manage.py syncdb --migrate

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
	pep8 --config=.pep8 analytics_dashboard
	cd analytics_dashboard && pylint --rcfile=../pylintrc $(PACKAGES)

	# Ignore module level docstrings and all test files
	#cd analytics_dashboard && pep257 --ignore=D100,D203 --match='(?!test).*py' $(PACKAGES)

validate_python: test.requirements test_python quality

validate_js:
	npm install
	gulp

validate: validate_python validate_js

demo:
	cd analytics_dashboard && ./manage.py switch show_engagement_forum_activity on --create

compile_translations:
	cd analytics_dashboard && i18n_tool generate

generate_fake_translations:
	cd analytics_dashboard && i18n_tool extract
	cd analytics_dashboard && i18n_tool dummy
	compile_translations
