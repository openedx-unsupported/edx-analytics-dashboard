.. _Courses_Page:

#######################
Overview of All Courses
#######################

Insights provides enrollment information about all of your courses in aggregate
as well as detailed information about enrollment, engagement, and other metrics
for each individual course. You find aggregate enrollment information, and
access individual courses, on the **Courses** page.

You can access the **Courses** page in the following ways.

* Sign in to Insights. The **Courses** page opens automatically.
* At the top of any Insights page, select **Insights**.

.. _Viewing Aggregate Enrollment Counts:

***********************************
Viewing Aggregate Enrollment Counts
***********************************

To view aggregate enrollment counts for your courses, open the **Courses** page
by signing in to Insights, or by selecting **Insights** at the top of any page.

At the top of the **Courses** page, cards show the following top-level
metrics across all of your courses.

* **Total Enrollment**: The number of past and current enrollments across all
  of your courses. Learners who have unenrolled in a course do not affect this
  number.
* **Current Enrollment**: The number of current enrollments in all of your
  courses.
* **Change in Last Week**: The net increase or decrease of enrollments across
  all of your courses over the past seven days.
* **Verified Enrollment**: The number of enrollments in the verified enrollment
  track across all of your courses.

.. _Course_List:

********************************************
Viewing Individual Course Enrollment Metrics
********************************************

On the **Courses** page, you can view enrollment metrics for all of your
courses in one place. This page contains the Course List table, which provides
the following information about each course.

* Course Name
* Course ID
* Course Start Date
* Course End Date
* Total Enrollment
* Current Enrollment
* Change Last Week
* Verified Enrollment

.. note::
 On Edge, the Course List table does not include the course name, start date,
 or end date.

For a quick view of information that's important to you, click the title of any
column to sort the Course List table by that column.

============================================
Identify Courses With the Highest Enrollment
============================================

If you want to find courses with the highest enrollment, you can sort the table
by either the “Total Enrollment” or “Current Enrollment” columns, depending on
the metric that you are interested in. This will help you understand which
courses attract the most learners.

You can sort by the “Verified Enrollment” column to find courses with the
highest number of verified learners.

===============================================
Identify Recent Enrollment Changes for a Course
===============================================

If you are running course marketing campaigns, you may be interested in looking
at recent changes in enrollment. If you sort by the “Change Last Week” column
in descending order, you can see the courses with the greatest increase in
enrollment in the past week. You will need to draw on your knowledge of recent
marketing efforts to interpret this data, and assess the impact of marketing
efforts on course enrollments.

=================================
Access Data for a Specific Course
=================================

To access Insights data for a specific course or courses, locate the name of
the course in the Course List table, and then select the course name.

To locate a course in the Course List table, you can use the options in the
left pane to limit the courses that the table lists. You can search by course
name or course ID, and you can filter by availability and pacing type. You can
also combine any of these options.

* In the **Find a Course** field, enter any part of the course name or course
  ID, and then click the search icon.
* Under **Availability** or **Pacing Type**, select the options that you want
  to include in your search. The list of courses updates automatically when you
  select or clear an option.

====================================
Access Data for Courses in a Program
====================================

To access Insights data for the courses in one or more specific programs, such
as XSeries and MicroMasters programs, locate **Programs** in the left pane, and
then select the program or programs that you want. The courses in the program
or programs then appear in the Course List table. You can use the Programs
filter in conjunction with other filters or searches to find the specific
courses that you are interested in.

************************************************
Viewing Detailed Enrollment Data for All Courses
************************************************

A Course Summary report that shows detailed information for all of your courses
is available for download. This report includes columns for course availability
and pacing type, two different counts for every enrollment mode, and other
information.

To download the Course Summary report in a comma-separated value (CSV) file,
select **Download CSV**.

.. note::
  The Course Summary report contains information for all of your courses, even
  if you select filters when you view the Course List table.

The CSV file contains the following columns.

* availability (shows whether the course is archived, current, or upcoming)
* catalog_course (shows the unique identifier for the course)
* catalog_course_title
* count
* count_change_7_days
* course_id (shows the unique identifier for a specific course run)
* cumulative_count
* end_date
* enrollment_modes.audit.count
* enrollment_modes.audit.cumulative_count
* enrollment_modes.credit.count
* enrollment_modes.credit.cumulative_count
* enrollment_modes.honor.count
* enrollment_modes.honor.cumulative_count
* enrollment_modes.professional.count
* enrollment_modes.professional.cumulative_count
* enrollment_modes.verified.count
* enrollment_modes.verified.cumulative_count
* pacing_type
* program_ids
* program_titles
* start_date

For detailed information about the computations in this report, see
:ref:`Enrollment Computations`. Note that the enrollment data that the
computations include is the same as the summary metrics presented in the
:ref:`Enrollment_Activity` report.
