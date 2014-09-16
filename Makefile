ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
PACKAGES = analytics_dashboard courses

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
	nosetests acceptance_tests --processes=2 --process-timeout=120


quality:
	pep8 --config=.pep8 analytics_dashboard
	cd analytics_dashboard && pylint --rcfile=../.pylintrc $(PACKAGES)

	# Ignore module level docstrings and all test files
	#cd analytics_dashboard && pep257 --ignore=D100,D203 --match='(?!test).*py' $(PACKAGES)

validate_python: test.requirements test_python quality

validate_js:
	npm install
	gulp

validate: validate_python validate_js

demo:
	cd analytics_dashboard && ./manage.py switch show_engagement_demo_interface on --create
	cd analytics_dashboard && ./manage.py switch navbar_display_engagement on --create
	cd analytics_dashboard && ./manage.py switch navbar_display_engagement_content on --create
	cd analytics_dashboard && ./manage.py switch navbar_display_overview on --create
	cd analytics_dashboard && ./manage.py switch show_engagement_forum_activity on --create


generate_fake_translations:
	cd analytics_dashboard && i18n_tool extract
	cd analytics_dashboard && i18n_tool dummy
	cd analytics_dashboard && i18n_tool generate
