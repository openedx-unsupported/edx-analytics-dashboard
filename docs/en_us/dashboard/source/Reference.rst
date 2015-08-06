.. _Reference:

#######################
Computation Reference
#######################

This chapter provides detailed information about how values presented by
edX Insights are computed. 

.. contents:: Section Contents 
  :local:
  :depth: 1

.. _All Computations:

*********************************
All Computations
*********************************

* Computations for the different metrics reported by edX Insights take place at
  different times. In addition, computations for reports and metrics that are
  available from the Instructor Dashboard of a course take place on a
  different schedule. As a result, differences can occur.

.. Jennifer asks for an x-ref to more information. Better place might be course_enrollment.rst in Running.

* All users who are enrolled in a course are included in the computations for
  that course. This means that in addition to the students, all of the course
  team members, beta testers, and discussion moderation team members are
  included.

.. spacer

* Account activation is not considered by the edX Insights computations. EdX
  Insights includes a learner who registers a user account and enrolls in a
  course, but does not activate the user account, in all computations as of
  the date and time of enrollment.

.. _Enrollment Computations:

*********************************
Enrollment Computations
*********************************

The number of enrolled students is computed every day, and the values reported
on the Enrollment Activity page in edX Insights are updated every day.

For information about viewing enrollment activity data in edX Insights, see
:ref:`Enrollment_Activity`.

**Enrollment metric**

* Users are included in the count as of the date and time they enroll in a
  course.

* Users who unenroll are excluded from the count as of the date and time they
  unenroll.

* The daily computations use the enrollment status of each user as of 23:59 UTC
  on the previous day.

* Course team members can enroll students from the **Membership** page in the
  Instructor Dashboard by supplying a list of email addresses or usernames.
  Actual resulting enrollments can occur on different dates, as follows.

 * When the **Auto Enroll** option is cleared, each student must manually
   complete the enrollment process for the course. Users are included as of the
   date and time they enroll.

 * When **Auto Enroll** is selected, each student who already has a user
   account is enrolled in the course and included in the count as of the date
   and time the initiating team member clicks **Enroll**.

   Students who are automatically enrolled in a course but have not yet
   registered a user account are included as of the date and time that they do
   register their user accounts.

**Enrollment Over Time chart**
  
* The filled area of this stacked area chart represents the 
  number of users who are currently enrolled in the course each day.

* The x-axis shows dates from course creation through the end of the last
  update period.

* The y-axis shows the number of currently enrolled users. 

* For courses that offer more than one enrollment option or certification
  track, different colors in the filled area represent the contribution of each
  option or track to the current enrollment count.

  In addition to honor code certificates, courses can offer a verified
  certificate option or enroll students through a professional education
  program.

* Each enrolled student is included in one, and only one, of the possible
  enrollment tracks on a given date. The student's enrollment track as of 23:59
  UTC is used each day.

**Enrollment Over Time report**

* If a course offers students the option to pursue a verified certificate, the
  report includes columns for **Verified Enrollment** and **Honor Code
  Enrollment**.
  
* If a course enrolls students through a professional education program, the
  report includes columns for **Professional Enrollment** and **Honor Code
  Enrollment**.

* The **Honor Code Enrollment** column reports the count of students who opted
  to receive an honor code certificate for the course.

  At one time, the edx.org site offered students options to "audit" the course
  only, or to audit the course and then receive an "honor" certificate when a
  passing grade was achieved. For courses that ran at that time, the **Honor
  Code Enrollment** column reports the sum of the students with these
  enrollment options.

.. _Demographic Computations:

*********************************
Demographic Computations
*********************************

During edX user account registration, students can provide demographic data
about themselves. Demographic distributions are computed every day to reflect
changes in course enrollment.

Currently, students make selections from drop-down lists on the edx.org and
edge.edx.org registration pages to provide demographic data.

* Students cannot change the selections that they make after registration is
  complete.

* Past versions of the registration pages used different options to collect
  demographic information. For example, the choices available to characterize
  educational background have been relabeled. EdX makes a best effort to
  normalize student responses to the labels that are currently being presented.

For information about viewing student demographic data in edX Insights, see
:ref:`Enrollment_Demographics`.

**Age chart**

* Students can select a year of birth. Student age is computed as the
  difference between the current year and the selected year of birth.

* Each bar in the histogram represents the number of enrolled users (y-axis) 
  of that age (x-axis).

* Students who did not provide a year of birth at registration are not
  represented in the histogram.

**Age band metrics**

* Computed student ages are grouped into three age bands: 0-25 years old, 26-40
  years old, and 41 years old and above.

* The percentage of students in each age band is computed from the number of
  enrolled students who provided a year of birth. Students who did not provide
  a year of birth at registration are not included.

**Educational Background chart**

* Students can select a highest level of education completed. 
  
* Each bar in the histogram represents the percentage of enrolled users
  (y-axis) who selected a completion level (x-axis).

* Percentages are calculated based on the number of currently enrolled students
  who reported an educational level, not on the total number of enrolled
  students.

* The table that follows shows each edX Insights label, the option that
  students can select at registration, and a brief description.
  
  .. list-table::
     :widths: 10 20 70
     :header-rows: 1

     * - edX Insights Label
       - Student Response
       - Description
     * - None
       - None
       - No formal education.
     * - Primary
       - Elementary/primary school
       - Initial schooling lasting approximately six years.
     * - Middle
       - Junior secondary/junior high/middle school
       - Continuing basic education lasting two to three years.
     * - Secondary
       - Secondary/high school
       - More specialized preparation for continuing education or employment
         lasting three to four years.
     * - Associate
       - Associate degree
       - Completion of two years of post-secondary education.
     * - Bachelor's
       - Bachelor's degree
       - Completion of four years of post-secondary education.
     * - Master's
       - Master's or professional degree
       - Certification for advanced academic or occupationally specific
         education.
     * - Doctorate
       - Doctorate
       - Advanced qualification for original research.

**Educational Background band metrics**

* Student educational backgrounds are grouped into three bands, as follows.
  
  .. list-table::
     :widths: 10 70
     :header-rows: 1

     * - Band
       - Student Response
     * - High school diploma or less
       - None, Elementary/primary school, Junior secondary/junior high/middle
         school, Secondary/high school
     * - College Degree
       - Associate degree, Bachelor's degree
     * - Advanced Degree
       - Master's or professional degree, Doctorate

* The percentage of students in each band is computed from the number of
  enrolled students who provided an educational level completed. Students who
  did not provide this information at registration are not included.

**Gender chart and report**

* Students can select a gender. The chart depicts the percentage of students
  who selected each choice (Female, Male, Other).

* The chart only includes students who reported their genders. The percentages
  shown in the chart are computed for currently enrolled students who did
  select a gender.

* The report includes all currently enrolled students. For each day, the report
  includes the daily enrollment count followed by columns that break down the
  enrollment count by Female, Male, Other, or Not Reported.

.. _Location Computations:

*********************************
Location Computations
*********************************

* The geographic locations of students are updated every day.

* User location is determined from the IP address used during interactions with
  course content. An ISO 3166 country code is associated with each IP address. 

* The last known location of each user, as of the end of the previous day, is
  used.

* User location is determined without regard to a specific course. Users who
  are enrolled in more than one course are identified as being in the same
  location for all of their courses.

For information about viewing geographic data in edX Insights, see
:ref:`Enrollment_Geography`.

**Geographic Distribution map**

* The number of users and the percentage of the current course enrollment is
  provided for each country.

* Users with IP addresses that cannot be located, or that result in a "non-
  country" code such as A1 (Anonymous Proxy), A2 (Satellite Provider), or O1
  (Other Country), are reported in an "Unknown" category.

* The computational frequency and approaches used to determine user location
  and user enrollment status are different. As a result, you might note
  discrepancies between the current number of students reported by the
  Enrollment Activity and Enrollment Geography sections of edX Insights.

**Total Countries Represented metric**

* The sum of the unique country codes identified from user IP addresses. 

* This total does not include "non-country" ISO codes such as A1, A2, or O1.

**Top Country by Enrollment metric** 

The country in which the largest number of users is located. The countries in
which the second and third largest numbers of users are located are identified
as well.

.. _Engagement Computations:

*********************************
Engagement Computations
*********************************

=================================
Content Engagement Computations
=================================

* The computations for engagement with course content are updated once a week,
  typically on Mondays.

* Computations are made on data collected through Sunday at 23:59 UTC (11:59
  pm).

* Changes over a one week period are computed for the period Monday at 00:00
  UTC through Sunday at 23:59 UTC.

* Measures of student engagement with course content identify the number of
  unique users who completed an activity during a week.

* Each unique user who engages in one of the categories of activity increases
  the count for that category by 1. A student who completes 10 problems
  increases the count of students who tried a problem by 1. The same student
  also increases the overall count of active students by 1.

For information about viewing engagement metrics in edX Insights, see
:ref:`Engagement_Content`.

**Active Students Last Week metric** 
  
* The number of unique users who visited any page in the course (a URL) at
  least once during the last update period.

  Some examples of the activities that a student can complete on a page, and
  that are included in this count, include contributing to a discussion topic,
  reading a textbook, submitting an answer to any type of problem, playing a
  video, and reviewing the course updates.

* This metric includes all course activities, excluding enrollment and
  unenrollment.  

**Watched a Video Last Week metric** 
  
* The number of unique users who clicked play for at least one of the course
  videos. 

* Only videos that were played on the edX platform video player are included.

**Tried a Problem Last Week metric** 
  
* The number of unique users who submitted an answer for at least one problem
  of these types:

  * Checkboxes (`<choiceresponse>`)
  * Dropdown (`<optionresponse>`)
  * Multiple choice (`<multiplechoiceresponse>`)
  * Numerical input (`<numericalresponse>`)
  * Text input (`<stringresponse>`)
  * Math expression input (`<formularesponse>`)

**Weekly Student Engagement graph**
  
* The markers on the graph represent the number of users who interacted with
  different aspects of the course each week.

* The x-axis includes computations made from course creation through the end of
  the last update period.

* Computations are updated weekly.

* The y-axis shows the number of unique users.

==============================
Video Engagement Computations
==============================

.. TBD: schedule and interval for updating video data

To compute data for video engagement, edX defines a video view as having both a
play video action and a companion pause video action or the automated stop that
occurs at the end of the video. 

* EdX Insights counts each play action at the 00:00 second that has a companion
  automated stop at the end of the video as a complete view of the video. 

* EdX Insights counts each five second segment that occurs between the play
  action and a pause or the stop as a complete view of that segment.

* Some normal user interactions, such as closing the browser window without
  explicitly pausing the video first, result in a play action without the
  necessary companion pause or stop action. As a result, the data that edX
  Insights presents can be considered a conservative estimate of the actual
  number of complete views.

For information about reviewing data for videos in edX Insights, see
:ref:`Engagement_Video`.

**Video Views stacked bar chart**

* Each bar in the histogram aggregates data for all of the video components in
  a section, subsection, or unit.

 * The x-axis shows the sections, subsections, or units in the course.

 * The y-axis shows the total number of times the video was viewed. The
   area shaded in green represents the number of complete views. The area
   shaded in gray represents the number of incomplete views.
  
**Total Video Views stacked area chart**

* The x-axis shows the duration of the video.

* The y-axis shows the number of play events. 

* The filled area of this stacked area chart represents the total number of
  times each five second segment of a video file has played.

 * The area shaded in lighter blue represents the number of unique users who
   played that segment of the video.

 * The area shaded in darker blue represents the number of additional views,
   or replays, of that segment of the video.

**Video metrics**

* The percentage of learners who started the video at its beginning and were
  playing it when it automatically stopped at the end of the file.

* The number of learners who started playing the video file.

* The number of learners who were playing the video when it automatically
  stopped at the end of the file.


.. _Performance Computations:

*****************************
Performance Computations
*****************************

* Student answer submission data is available only for problems of these
  types.

  * Checkboxes (``<choiceresponse>``)
  * Dropdown (``<optionresponse>``)
  * Multiple choice (``<multiplechoiceresponse>``)
  * Numerical input (``<numericalresponse>``)
  * Text input (``<stringresponse>``)
  * Math expression input (``<formularesponse>``)
  
  For information about the problem types that can be included in courses and
  their settings, see `Creating Exercises and Tools`_.

* For data to be available for a problem, at least one student must
  have submitted an answer for that problem after 6 Mar 2014.

* Computations are updated daily. 

* Only a student's last submission is included in the computation. Any
  attempts prior to the last submission are not included.

* Computations for graded content include only problems for which students can
  click **Check** to submit their responses. If students can only save their
  responses without submitting them (that is, if the **Maximum Attempts** for
  the problem is set to 0), data is not available for student submission
  computations.

* Only problem activity that occurred after 23 Oct 2013 is included. 

**Graded Content Submissions .csv file**

The .csv file contains a superset of the data that is included in the
Submission Counts chart and report. The .csv file contains the following columns.

.. list-table::
   :widths: 20 60
   :header-rows: 1

   * - Column
     - Description
   * - ``answer_value``
     - The text label of the answer choice for checkboxes, dropdown, and
       multiple choice problems. The value entered by the student for text
       input, numerical input, and math expression input problems. 

       Answer choices selected by at least one student after 23 Oct 2013, but
       not selected after 6 Mar 2014, do not include an ``answer_value`` for
       checkboxes and multiple choice problems. The ``value_id`` is available
       for these problems.

   * - ``consolidated_variant``
     - TRUE if the Studio **Randomization** setting for this problem component
       is set to **Always**, **On Reset**, or **Per Student**, but there is no
       variation in the possible answers. Often, this indicates that the
       Python script that randomizes values for the problem is not present.
       
       FALSE if the Studio **Randomization** setting for this problem
       component is set to **Never** (the default) or if the Python script is
       randomizing values.

   * - ``correct``
     - TRUE if this answer value is correct. FALSE if this answer value is
       incorrect.
   * - ``count``
     - The number of students who entered or selected this answer as
       their most recent submission for the problem or problem variant. 

       The count reflects the entire problem history. If you change a 
       problem after it is released, it might not be possible for you to 
       determine which answers were given before and after you made the change.

   * - ``course_id``
     - The identifier for the course run.
   * - ``created``
     - The date and time of the computation.
   * - ``module_id``
     - The internal identifier for the problem component.
   * - ``part_id``
     - For a problem component that contains multiple questions, the internal
       identifier for each question. For a problem component that contains a
       single question, the internal identifier of that problem.
   * - ``problem_display_name``
     - The display name defined for the problem.
   * - ``question_text``
     - The accessible label that appears above the answer choices or
       the value entry field for the problem. In the Studio Simple Editor, this
       text is surrounded by two pairs of angle brackets (>>Question<<). Blank
       for questions that do not have an accessible label.

       For problems that use the **Randomization** setting in Studio, if a
       particular answer has not been selected since 6 Mar 2014, the
       ``question_text`` is blank for that answer.

   * - ``value_id``
     - The internal identifier for the answer choice provided for checkboxes
       and multiple choice problems. Blank for dropdown, numerical input, text
       input, and math expression input problems.
   * - ``variant``
     - For problems that use the **Randomization** setting in Studio, the
       unique identifier for a variant of the problem. Blank for problems that
       have this setting defined as **Never** (the default).


After you download the .csv file, be aware that different spreadsheet
applications can display the same data in different ways.

* Not all spreadsheet applications interpret and render UTF-8 encoded
  characters correctly.

* Some spreadsheet applications alter data for display purposes, such as
  inserting zeroes into numbers expressed as decimals. For example, the
  student answer ".5" can be appear in a spreadsheet as "0.5".

If you notice characters that do not display as expected, or multiple lines
that have the same ``answer_value`` but different counts, try opening the file
in a different spreadsheet application or a text editor.

.. _Error Conditions:

*****************
Error Conditions
*****************

The data that edX collects from student interactions has expanded over time to
capture increasingly specific information, and continues to expand as we add
new features to the platform. As a result, more data is available for courses
that are running now, or that ran recently, than for courses that ran in the
past. Not all data for every value reported by edX Insights is available for
every course run.

In the following situations, data might not be available in edX Insights. 

* EdX changed the method used to track student enrollments on 3 Dec 2013.
  For courses created in Studio prior to 4 Dec 2013, edX Insights reports
  enrollment activity beginning with the enrollment count on 11 Nov 2013.

* For courses with a very small number of enrolled users, such as newly created
  courses, data for enrollment activity, enrollment geography, or both, might
  not be available.

* For courses that do not have any recorded student interactions, such as test
  courses and courses that finished running early in the history of the edX
  platform, data for enrollment activity and student engagement might not be
  available.

* Charts are not available for problems that use the **Randomization** setting
  in Studio. Because such problems can result in numerous possible submission
  variants, both correct and incorrect, edX Insights does not attempt to graph
  them. The Submissions report and downloadable .csv file are available for
  such problems, and include one row for each problem-variant-answer
  combination selected by your students.


.. _Creating Exercises and Tools: http://edx.readthedocs.org/projects/edx-partner-course-staff/en/latest/exercises_tools/index.html