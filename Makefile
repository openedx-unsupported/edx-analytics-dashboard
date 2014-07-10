ROOT = $(shell echo "$$PWD")
COVERAGE = $(ROOT)/build/coverage
PACKAGES = analytics_dashboard

clean:
	find . -name '*.pyc' -delete
	coverage erase

test: clean
	cd analytics_dashboard && ./manage.py test --settings=analytics_dashboard.settings.test \
		--exclude-dir=analytics_dashboard/settings --with-coverage --cover-inclusive --cover-branches \
		--cover-html --cover-html-dir=$(COVERAGE)/html/ \
		--cover-xml --cover-xml-file=$(COVERAGE)/coverage.xml \
		--cover-package=$(PACKAGES) \
		$(PACKAGES)
