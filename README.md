Part of [Open edX](https://open.edx.org/)

edX Analytics Dashboard [![BuildStatus](https://travis-ci.org/edx/edx-analytics-dashboard.svg?branch=master)](https://travis-ci.org/edx/edx-analytics-dashboard) [![CoverageStatus](https://img.shields.io/coveralls/edx/edx-analytics-dashboard.svg)](https://coveralls.io/r/edx/edx-analytics-dashboard?branch=master)
=======================
Dashboard to display course analytics to course teams

Prerequisites
-------------
* Python 2.7.x (not tested with Python 3.x)
* [gettext](http://www.gnu.org/software/gettext/)
* [node](https://nodejs.org) 5.2.x
* [npm](https://www.npmjs.org/)
* [JDK 7+](http://openjdk.java.net/)

Getting Started
---------------
1. Get the code (e.g. clone the repository).
2. Install the Python/Node/Bower requirements:

        $ make develop

3. Setup your database:

        $ make migrate

4. Run the server:

        $ ./manage.py runserver 0.0.0.0:9000

By default the Django Default Toolbar is disabled. To enable it set the environmental variable ENABLE_DJANGO_TOOLBAR.

Alternatively, you can launch the server using:

        $ ENABLE_DJANGO_TOOLBAR=1 ./manage.py runserver


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

The following flags are available:

| Flag                           | Purpose                                               |
|--------------------------------|-------------------------------------------------------|
| display_learner_analytics      | Display Learner Analytics links                       |

Authentication & Authorization
------------------------------
By default, this application relies on an external OAuth2/Open ID Connect provider
(contained within the [LMS](https://github.com/edx/edx-platform)) for authentication and authorization. If you are a
developer, and do not want to setup edx-platform, you can get around this requirement by doing the following:

1. Set `ENABLE_AUTO_AUTH` to `True` in your settings file. (This is the default value in `settings/local.py`).
2. Set `ENABLE_COURSE_PERMISSIONS` to `False` in your settings file.
3. Visit `http://localhost:9000/test/auto_auth/` to create and login as a new user.

Note: When using Open ID Connect, the dashboard and provider must be accessed via different host names
(e.g. dashboard.example.org and provider.example.org) in order to avoid issues with session cookies being overwritten.

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
Static files are managed via [django-compressor](http://django-compressor.readthedocs.org/) and [RequireJS](http://requirejs.org/).
RequireJS (and r.js) are used to manage JavaScript dependencies. django-compressor compiles SASS, minifies JavaScript (
using [Closure Compiler](https://developers.google.com/closure/compiler/)), and handles naming files to facilitate
cache busting during deployment.

Both tools should operate seamlessly in a local development environment. When deploying to production, call
`make static` to compile all static assets and move them to the proper location to be served.

When creating new pages that utilize RequireJS dependencies, remember to use the `static_rjs` templatetag to load
the script, and to add a new module to `build.js`.

Theming and Branding
--------------------
We presently have support for basic branding of the logo displayed in the header and on error pages. This is facilitated
by including an additional SCSS file specifying the path and dimensions of the logo. The default Open edX theme located
at `static/sass/themes/open-edx.scss` is a good starting point for those interested in changing the logo. Once your
customizations are complete, update the value of the setting `THEME_SCSS` with the path to your new SCSS file.

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

How to Contribute
-----------------

Contributions are very welcome, but for legal reasons, you must submit a signed
[individual contributor's agreement](http://code.edx.org/individual-contributor-agreement.pdf)
before we can accept your contribution. See our
[CONTRIBUTING](https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst)
file for more information -- it also contains guidelines for how to maintain
high code quality, which will make your contribution more likely to be accepted.

### JavaScript Code Quality
JavaScript developers should adhere to the [edX JavaScript standards](https://github.com/edx/edx-platform/wiki/Javascript-standards-for-the-edx-platform).
These standards are enforced using [JSHint](http://www.jshint.com/) and [jscs](https://www.npmjs.org/package/jscs).

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
Please do not report security issues in public. Please email security@edx.org.


Mailing List and IRC Channel
----------------------------
You can discuss this code on the [edx-code Google Group](https://groups.google.com/forum/#!forum/edx-code) or in the
`edx-code` IRC channel on Freenode.
