Part of [edX code](http://code.edx.org/)

edX Analytics Dashboard
=======================
Dashboard to display course analytics to course teams

Getting Started
---------------
1. Get the code (e.g. clone the repository).
2. Install the Python requirements:

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
(switch)[http://waffle.readthedocs.org/en/latest/types.html#switches]:

        $ ./manage.py switch feature_name [on/off] --create

See the [Waffle documentation](http://waffle.readthedocs.org/en/latest/) for details on utilizing features in code and templates.

The following switches are available:

| Switch                            | Purpose                                                  |
|-----------------------------------|----------------------------------------------------------|
| show_engagement_demo_interface    | Show experimental content below the engagement summary   |
| navbar_display_engagement         | Show the engagement item in the lens drop down           |
| navbar_display_engagement_content | Show the "Content" sub-section in the engagement nav bar |
| navbar_display_overview           | Show the overview item in the lens drop down             |

Authentication & Authorization
------------------------------
By default, this application relies on an external OAuth2/Open ID Connect provider 
(contained within the [LMS](https://github.com/edx/edx-platform)) for authentication and authorization. If you are a 
developer, and do not want to setup edx-platform, you can get around this requirement by doing the following:

1. Set `ENABLE_AUTO_AUTH` to `True` in your settings file. (This is the default value in `settings/local.py`).
2. Set `ENABLE_COURSE_PERMISSIONS` to `False` in your settings file.
3. Visit `http://localhost:9000/test/auto_auth/` to create and login as a new user. 

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
| TEST_PASSWORD            | password used to login to the app     | edx                              |


Override example:

        $ DASHBOARD_SERVER_URL="http://example.com" API_SERVER_URL="http://api.example.com" API_AUTH_TOKEN="example" make accept


Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@edx.org.


Mailing List and IRC Channel
----------------------------
You can discuss this code on the [edx-code Google Group](https://groups.google.com/forum/#!forum/edx-code) or in the `edx-code` IRC channel on Freenode.
