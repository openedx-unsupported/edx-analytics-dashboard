Part of [edX code](http://code.edx.org/)

edX Analytics Dashboard
=======================
Dashboard to display course analytics to course teams

Getting Started
---------------
1. Get the code (e.g. clone the repository).
2. Install the Python requirements:

        $ pip install -r requirements/devtest.txt

3. Change to the Django project directory.

        $ cd analytics_dashboard

4. Setup your database:

        $ ./manage.py syncdb --migrate

5. Run the server:

        $ ./manage.py runserver

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
    $ cd analytics-dashboard
    $ ./manage.py test

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
