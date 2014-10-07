Part of [edX code](http://code.edx.org/)

edX Analytics Dashboard [![BuildStatus](https://travis-ci.org/edx/edx-analytics-dashboard.svg?branch=master)](https://travis-ci.org/edx/edx-analytics-dashboard) [![CoverageStatus](https://img.shields.io/coveralls/edx/edx-analytics-dashboard.svg)](https://coveralls.io/r/edx/edx-analytics-dashboard?branch=master)
=======================
Dashboard to display course analytics to course teams

Prerequisites
-------------
* Python 2.7.x (not tested with Python 3.x)
* [gettext](http://www.gnu.org/software/gettext/)
* [npm](https://www.npmjs.org/) 

Getting Started
---------------
1. Get the code (e.g. clone the repository).
2. Install the Python/Node/Bower requirements:

        $ make develop

3. Setup your database:

        $ make syncdb

4. Run the server:

        $ cd analytics_dashboard
        $ ./manage.py runserver 0.0.0.0:9000

By default the Django Default Toolbar is disabled. To enable it set the environmental variable ENABLE_DJANGO_TOOLBAR.

Alternatively, you can launch the server using:

        $ ENABLE_DJANGO_TOOLBAR=1 ./manage.py runserver


Feature Gating
--------------
Need a fallback to disable a feature? Create a [Waffle](http://waffle.readthedocs.org/en/latest/)
[switch](http://waffle.readthedocs.org/en/latest/types.html#switches):

        $ ./manage.py switch feature_name [on/off] --create

See the [Waffle documentation](http://waffle.readthedocs.org/en/latest/) for
details on utilizing features in code and templates.

The following switches are available:

| Switch                            | Purpose                                                  |
|-----------------------------------|----------------------------------------------------------|
| show_engagement_forum_activity    | Show the forum activity on the course engagement page    |

Authentication & Authorization
------------------------------
By default, this application relies on an external OAuth2/Open ID Connect provider 
(contained within the [LMS](https://github.com/edx/edx-platform)) for authentication and authorization. If you are a 
developer, and do not want to setup edx-platform, you can get around this requirement by doing the following:

1. Set `ENABLE_AUTO_AUTH` to `True` in your settings file. (This is the default value in `settings/local.py`).
2. Set `ENABLE_COURSE_PERMISSIONS` to `False` in your settings file.
3. Visit `http://localhost:9000/test/auto_auth/` to create and login as a new user. 

Internationalization (i18n)
---------------------------
In order to work with translations you must have you must have [gettext](http://www.gnu.org/software/gettext/) installed. gettext
 should be available via your preferred package manager (e.g. `yum`, `apt-get`, 'brew`, or `ports`).
###Development###
When adding or updating code, you should ensure all necessary strings are marked for translation. We have provided a
command that will generate dummy translations to help with this. This will create an "Esperanto" translation that is 
actually over-accented English.

        $ make generate_fake_translations

Restart your server after running the command above and update your browser's language preference to Esperanto (eo). 
Navigate to a page and verify that you see fake translations. If you see plain English instead, your code is not being 
properly translated.

###Updating Translations###
Once development is complete, translation source files (.po) must be generated. The command below handle this.

        $ cd analytics_dashboard && i18n_tool extract
        
The generated files located in `analytics_dashboard/conf/locale/en/LC_MESSAGES` should be uploaded to 
the [analytics-dashboard](https://www.transifex.com/projects/p/edx-platform/resource/analytics-dashboard/) and
[analytics-dashboard-js](https://www.transifex.com/projects/p/edx-platform/resource/analytics-dashboard-js/) resources 
at Transifex where translators will begin the translation process. This task can be completed using the [Transifex
Client](http://docs.transifex.com/developer/client/):

        $ tx push -s

Once translations are completed, run the commands below to download and compile the translations:

        $ tx pull -a
        $ cd analytics_dashboard && i18n_tool generate

Note that only the following files (for each language) should be committed to this repository:

* django.mo
* django.po
* djangojs.mo
* djangojs.po


License
-------
The code in this repository is licensed under version 3 of the AGPL unless otherwise noted.

Please see `LICENSE.txt` for details.

How to Contribute
-----------------

Contributions are very welcome, but for legal reasons, you must submit a signed
[individual contributor's agreement](http://code.edx.org/individual-contributor-agreement.pdf)
before we can accept your contribution. See our
[CONTRIBUTING](https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst)
file for more information -- it also contains guidelines for how to maintain
high code quality, which will make your contribution more likely to be accepted.

Testing
-------

### Unit Tests & Code Quality
The complete unit test and quality suite can be run with:

        $ make validate

The Python portion of this project uses `nose` to find and run tests. `pep8` and `pylint` are used to verify code 
quality. All three can be run with the command below:

        $ make validate_python


JavaScript tests and linting can be run with the following command:

        $ make validate_js
        
#### Continuous Integration (CI) Reports
The commands above will generate coverage reports the `build` directory. Python reports are located in `build/coverage`. 
 JavaScript reports are in `build/coverage-js`. Both should have a [Cobertura](http://cobertura.github.io/cobertura/) 
 `coverage.xml` file and an `html` directory with a human-readable HTML site.


### Acceptance Tests
The acceptance tests are designed to test the application as whole (contrasted with unit tests that test individual
components). These tests load the application in a browser and verify that data and elements appear as expected.

The Bash script `runAcceptance.sh` will start the Django server and run the tests against the server. After the tests
are run the server will be shutdown. Simply run the command below:

        $ ./runAcceptance.sh

If you already have a server running, there is also a make task you can run instead of the script above.

        $ make accept

The tests make a few assumptions about URLs and authentication. These can be overridden by setting environment variables
when executing either of the commands above.

| Variable                 | Purpose                               | Default Value                    |
|--------------------------|---------------------------------------|----------------------------------|
| DASHBOARD_SERVER_URL     | URL where the dashboard is served     | http://127.0.0.1:9000            |
| API_SERVER_URL           | URL where the analytics API is served | http://127.0.0.1:9001/api/v0     |
| API_AUTH_TOKEN           | Analytics API authentication token    | edx                              |
| DASHBOARD_FEEDBACK_EMAIL | Feedback email in the footer          | override.this.email@example.com  |
| TEST_USERNAME            | Username used to login to the app     | edx                              |
| TEST_PASSWORD            | Password used to login to the app     | edx                              |
| PLATFORM_NAME            | Platform/organization name            | edX                              |
| APPLICATION_NAME         | Name of this application              | Insights                         |
| SUPPORT_URL              | URL where error pages should link     | http://example.com/              |


Override example:

        $ DASHBOARD_SERVER_URL="http://example.com" API_SERVER_URL="http://api.example.com" API_AUTH_TOKEN="example" make accept

#### Course Validation
In addition to the standard acceptance tests, there is also a script to validate all course pages and report their
HTTP status codes. Use the command below to execute this script.

        $ make course_validation


Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@edx.org.


Mailing List and IRC Channel
----------------------------
You can discuss this code on the [edx-code Google Group](https://groups.google.com/forum/#!forum/edx-code) or in the 
`edx-code` IRC channel on Freenode.
