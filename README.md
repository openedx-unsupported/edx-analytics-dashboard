analytics-dashboard
===================

Dashboard to display course analytics to course teams

Prerequisites
-------------

You will need the following component(s) installed on your machine:

* node/npm
* bowerd

Getting Started
---------------

1. Get the code (e.g. clone the repository).
2. Install the node requirements:

        $ npm install

3. Install the Python requirements:

        $ pip install -r requirements/local.txt

4. Change to the Django project directory.

        $ cd analytics_dashboard

5. Install the bower requirements:

        $ ./manage.py bower install

6. Run the server:

        ./manage.py runserver

Testing
-------

    $ ./manage.py test
