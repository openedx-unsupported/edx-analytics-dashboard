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

### Python Tests

1. Change to project directory if you haven't already:

        $ cd analytics_dashboard

2. Run unit tests:

        $ ./manage.py test

3. Update address and port in ACCEPTANCE_TEST_SERVER in analytics_dashboard/settings/local.py if you're not using the defaults.

4. Run acceptance tests:

        $ ./runAcceptance.sh

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
