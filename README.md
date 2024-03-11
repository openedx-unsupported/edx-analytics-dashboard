edX Analytics Dashboard
=======================
Dashboard to display course analytics to course teams

# DEPRECATION NOTICE

The Insights product and associated repositories are in the process of being 
deprecated and removed from service. Details on the deprecation status and
process can be found in the relevant [Github issue](https://github.com/openedx/public-engineering/issues/221).

This repository may be archived and moved to the openedx-unsupported
Github organization at any time.

The following sections are for historical purposes only.

---

Prerequisites
-------------
* Python 3.8.x
* [gettext](http://www.gnu.org/software/gettext/)
* [node](https://nodejs.org) 12.11.1
* [npm](https://www.npmjs.org/) 6.11.3

Warning: You must have NPM version 5.5.1. Using another version might result in
a different `package-lock.json` file. Committing those changes might break our
deployments which use NPM 5.5.1 and expect no changes after running `npm
install`. [nodeenv](https://github.com/ekalinin/nodeenv) or
[n](https://github.com/tj/n) are tools that you can use to work on different
Node.js and NPM versions than your system installed versions.

It's recommended you set up this service with devstack so
that you will not have to manage Node and NPM versions yourself.

Getting Started With Devstack
-----------------------------
The best way to run this service is with edX Devstack: https://github.com/openedx/devstack.

See the [Devstack README](https://github.com/openedx/devstack/blob/master/README.rst) for information on how to install and run Insights. For the purposes of devstack this service will be referred to as `insights` and not `analytics-dashboard`.

Provisioning for insights and the data api can be combined:

.. code:: sh

make dev.provision.insights+analyticsapi

Getting Started Standalone
--------------------------
1. Get the code (e.g. clone the repository).
2. Create a Python 3 virtual environment and activate it
2. Install the Python/Node requirements:

        $ make develop

3. Setup your database:

        $ make migrate

4. Run the webpack-dev-server:

        $ npm start

If you plan on running the Django development server on a different port or
host, make sure to set the `DJANGO_DEV_SERVER` environmental variable. For
example:

        $ DJANGO_DEV_SERVER='http://localhost:9000' npm start

5. In a separate terminal run the Django development server:

        $ ./manage.py runserver 0.0.0.0:8110

By default the Django Default Toolbar is disabled. To enable it set the environmental variable ENABLE_DJANGO_TOOLBAR.

Alternatively, you can launch the server using:

        $ ENABLE_DJANGO_TOOLBAR=1 ./manage.py runserver

Visit http://localhost:9000 in your browser and then login through the LMS to
access Insights (see **Authentication & Authorization** below for more details).

Site-Wide Announcements
-----------------------
Site-wide announcements are facilitated by
[pinax-announcements](https://github.com/pinax/pinax-announcements/blob/master/docs/index.md).
Use the admin site to manage announcements and dismissals.

Feature Gating
--------------
Need a fallback to disable a feature? Create a [Waffle](http://waffle.readthedocs.org/en/latest/)
[switch](http://waffle.readthedocs.org/en/latest/types/switch.html):

        $ ./manage.py waffle_switch name-of-my-switch on --create

See the [Waffle documentation](http://waffle.readthedocs.org/en/latest/) for
details on utilizing features in code and templates.

The following switches are available:

| Switch                               | Purpose                                               |
|--------------------------------------|-------------------------------------------------------|
| show_engagement_forum_activity       | Show the forum activity on the course engagement page |
| enable_course_api                    | Retrieve course details from the course API           |
| enable_ccx_courses                   | Display CCX Courses in the course listing page.       |
| enable_engagement_videos_pages       | Enable engagement video pages.                        |
| enable_video_preview                 | Enable video preview.                                 |
| display_course_name_in_nav           | Display course name in navigation bar.                |
| enable_performance_learning_outcome  | Enable performance section with learning outcome breakdown (functionality based on tagging questions in Studio) | 
| enable_learner_download              | Display Download CSV button on Learner List page.     |
| enable_problem_response_download     | Enable downloadable CSV of problem responses          |
| enable_course_filters                | Enable filters (e.g. pacing type) on courses page.    |
| enable_course_passing                | Enable passing column on courses page.                |

[Waffle](http://waffle.readthedocs.org/en/latest/) flags are used to disable/enable
functionality on request (e.g. turning on beta functionality for superusers). Create a
[flag](http://waffle.readthedocs.io/en/latest/usage/cli.html#flags):

        $ ./manage.py waffle_flag name-of-my-flag --everyone --create

Settings describe features which are not expected to be toggled on and off without significant system changes.

The following setting is available:

| Flag                           | Purpose                                               |
|--------------------------------|-------------------------------------------------------|
| ENROLLMENT_AGE_AVAILABLE      | Display age as part of enrollment demographics                       |


Authentication & Authorization
------------------------------
This section is only necessary if running I stand alone service OAuth2 is automatically configured by provisioning in devstack.

By default, this application relies on an external OAuth2 provider
(contained within the [LMS](https://github.com/openedx/edx-platform)) for authentication and authorization. If you are a
developer, and do not want to setup edx-platform, you can get around this requirement by doing the following:

1. Set `ENABLE_AUTO_AUTH` to `True` in your settings file. (This is the default value in `settings/local.py`).
2. Set `ENABLE_COURSE_PERMISSIONS` to `False` in your settings file.
3. Visit `http://localhost:9000/test/auto_auth/` to create and login as a new user.

Note: When using OAuth2, the dashboard and provider must be accessed via different host names
(e.g. dashboard.example.org and provider.example.org) in order to avoid issues with session cookies being overwritten. (This was true with the use of the removed Open ID Connect, but is untested since.)

Note 2: Seeing signature expired errors upon login? Make sure the clocks of your dashboard and OAuth servers are synced
with a centralized time server. If you are using a VM, the VM's clock may skew when the host is suspended. Restarting
the NTP service usually resolves this issue.

Internationalization (i18n)
---------------------------
In order to work with translations you must have you must have [gettext](http://www.gnu.org/software/gettext/) installed. gettext
 should be available via your preferred package manager (e.g. `yum`, `apt-get`, `brew`, or `ports`).
###Development###
When adding or updating code, you should ensure all necessary strings are marked for translation. We have provided a
command that will generate dummy translations to help with this. This will create an "Esperanto" translation that is
actually over-accented English.

        $ make generate_fake_translations

Restart your server after running the command above and update your browser's language preference to Esperanto (eo).
Navigate to a page and verify that you see fake translations. If you see plain English instead, your code is not being
properly translated.

###Updating Translations###
Once development is complete, translation source files (.po) must be generated. The command below will generate the
necessary source files and verify that an updated is needed:

        $ make validate_translations

If not [automated](https://docs.transifex.com/projects/updating-content#automatic-updates), the generated files located
in `analytics_dashboard/conf/locale/en/LC_MESSAGES` should be uploaded to the
[analytics-dashboard](https://www.transifex.com/projects/p/edx-platform/resource/analytics-dashboard/) and
[analytics-dashboard-js](https://www.transifex.com/projects/p/edx-platform/resource/analytics-dashboard-js/) resources
at Transifex where translators will begin the translation process. This task can be completed using the [Transifex
Client](http://docs.transifex.com/developer/client/):

        $ tx push -s

Once translations are completed, run the commands below to download and compile the translations:

        $ make pull_translations

Note that only the following files (for each language) should be committed to this repository:

* django.mo
* django.po
* djangojs.mo
* djangojs.po


Asset Pipeline
--------------
Static files are managed via [webpack](https://webpack.js.org/).

To run the webpack-dev-server, which will watch for changes to static files
(`.js`, `.css`, `.sass`, `.underscore`, etc. files) and incrementally recompile
webpack bundles and try to hot-reload them in your browser, run this in a
terminal:

    $ npm start

Alternatively, you can compile production webpack bundles by running (runs
webpack using the prod config and then exits):

    $ make static

Before committing new JavaScript, make sure it conforms to our style guide by
running [eslint](http://eslint.org/), and fixing any errors.

    $ npm run lint -s

You can also try automatically fixing the errors and applying an additional
level of standardized formatting with
[prettier](https://github.com/prettier/prettier) by running
[prettier-eslint](https://github.com/prettier/prettier-eslint).

    $ npm run format

Note: this will only format a subset of the JavaScript, we haven't converted the
formatting of all of our files yet. Edit the directory list in `package.json`.

Theming and Branding
--------------------
We presently have support for basic branding of the logo displayed in the header and on error pages. This is facilitated
by including an additional SCSS file specifying the path and dimensions of the logo. The default Open edX theme located
at `static/sass/themes/open-edx.scss` is a good starting point for those interested in changing the logo. Once your
customizations are complete, update the value of the yaml configuration setting `INSIGHTS_THEME_SCSS` with the path to
your new SCSS file. If running Webpack manually, you will have to set the environmental variable `THEME_SCSS` to your
file before running Webpack.

Developers may also choose to further customize the site by changing the variables loaded by SCSS. This is most easily
accomplished via the steps below. This will allow for easily changing basic colors and spacing.

        1. Copy `static/sass/_config-variables.scss` to a new file (e.g. static/sass/_config-variables-awesome-theme).
        2. Modify your variable values, but not the names, to correspond with your theme.
        3. Update `static/sass/style-application.scss` to load your file immediately after loading `config-variables`.

We welcome contributions from those interested in further expanding theming support!

License
-------
The code in this repository is licensed under version 3 of the AGPL unless otherwise noted.

Please see `LICENSE.txt` for details.

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

| Variable                     | Purpose                                    | Default Value                    |
|------------------------------|--------------------------------------------|----------------------------------|
| DASHBOARD_SERVER_URL         | URL where the dashboard is served          | http://127.0.0.1:9000            |
| API_SERVER_URL               | URL where the analytics API is served      | http://127.0.0.1:9001/api/v0     |
| API_AUTH_TOKEN               | Analytics API authentication token         | edx                              |
| DASHBOARD_FEEDBACK_EMAIL     | Feedback email in the footer               | override.this.email@example.com  |
| TEST_USERNAME                | Username used to login to the app          | edx                              |
| TEST_PASSWORD                | Password used to login to the app          | edx                              |
| PLATFORM_NAME                | Platform/organization name                 | edX                              |
| APPLICATION_NAME             | Name of this application                   | Insights                         |
| SUPPORT_EMAIL                | Email where error pages should link        | support@example.com              |
| ENABLE_COURSE_API            | Indicates if the course API is enabled on the server being tested. Also, determines if course performance tests should be run. | False     |
| GRADING_POLICY_API_URL       | URL where the grading policy API is served | (None)                           |
| COURSE_API_URL               | URL where the course API is served         | (None)                           |
| COURSE_API_KEY               | API key used to access the course API      | (None)                           |
| ENABLE_OAUTH_TESTS           | Test the OAUTH sign-in process             | true                             |
| ENABLE_AUTO_AUTH             | Sign-in using auto-auth. (no LMS involved) | false                            |
| ENABLE_COURSE_LIST_FILTERS   | Tests on filtering the course list         | false                            |
| ENABLE_COURSE_LIST_PASSING   | Tests on the passing learners column in the course list | false               |


Override example:

        $ DASHBOARD_SERVER_URL="http://example.com" API_SERVER_URL="http://api.example.com" API_AUTH_TOKEN="example" make accept

#### Course Validation
In addition to the standard acceptance tests, there is also a script to validate all course pages and report their
HTTP status codes. Use the command below to execute this script.

        $ make course_validation


Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@openedx.org.
