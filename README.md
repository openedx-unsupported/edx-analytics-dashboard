Part of [edX code](http://code.edx.org/)

edX Analytics Dashboard
=======================
Dashboard to display course analytics to course teams

Getting Started
---------------
1. Get the code (e.g. clone the repository).
2. Install the Python requirements:

        $ pip install -r requirements/local.txt
        $ pip install -r requirements/test.txt

3. Change to the Django project directory.

        $ cd analytics_dashboard

4. Setup your database:

        $ ./manage.py syncdb --migrate

5. Run the server:

        $ ./manage.py runserver

By default the Django Default Toolbar is disabled. To enable it set the environmental variable ENABLE_DJANGO_TOOLBAR.

Alternatively, you can launch the server using:

        $ ENABLE_DJANGO_TOOLBAR=1 ./manage.py runserver

License
-------
The code in this repository is licensed under version 3 of the AGPL unless otherwise noted.

Please see `LICENSE.txt` for details.

How To Contribute
-----------------
Contributions are very welcome.

Please read [How To Contribute](https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst) for details.

Testing
-------

### Unit Tests
This project uses `nose` to find and run tests. Execute the command below from the root of the repository to run tests.

    $ make test

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

| Variable             | Purpose                               | Default Value                |
|----------------------|---------------------------------------|------------------------------|
| DASHBOARD_SERVER_URL | URL where the dashboard is served     | http://127.0.0.1:8000        |
| API_SERVER_URL       | URL where the analytics API is served | http://127.0.0.1:8001/api/v0 |
| API_AUTH_TOKEN       | Analytics API authentication token    | analytics                    |


Override example:

        $ DASHBOARD_SERVER_URL="http://example.com" API_SERVER_URL="http://api.example.com" API_AUTH_TOKEN="example" make accept

### JavaScript Tests

1. Install node.js packages (if you haven't run this already):

        $ npm install

2. Run default gulp tasks:

        $ gulp

3. Run the JavaScript tests alone:

        $ gulp test

4. Run the JavaScript linting alone:

        $ gulp lint


Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@edx.org.


Mailing List and IRC Channel
----------------------------
You can discuss this code on the [edx-code Google Group](https://groups.google.com/forum/#!forum/edx-code) or in the `edx-code` IRC channel on Freenode.
