1. Only Aggregated Learner Data In Analytics
--------------------------------------------

Status
------

Accepted

Context
-------

Since the learner view is the most expensive to support and one of the least used we are deprecating it. That creates an opportunity to better define what analytics data is allowed in the analytics dashboard.

Most reports in Insights provide aggregate user data with the exception of the learners report. That report includes username, email address, and individual performance information.

Personally identifiable information (PII) belonging to learners requires more careful treatment than aggregated learner data. Individual performance is also more sensitive than averages or aggregates.


Decision
--------

Inights will not contain any personally identifiable learner information such as names or emails. Further, the analytics dashboard will only display aggregate or average information across a class of learners. Individual performance or other behavior will not be part of Insights.

Consequences
------------

The learners report has been deprecated and removed from Insights.

This decision constrains future Insights reports to only aggregate data. If we want to expose individual learner data to instructors, we will use a different channel with access control appropriate to more sensitive information.


References
----------

- `Learner view removal discussion <https://discuss.openedx.org/t/deprecation-removal-learner-view-in-insights-data-api-and-analytics-pipeline/6788>`_
- `Learner view DEPR ticket <https://github.com/openedx/public-engineering/issues/36>`_
