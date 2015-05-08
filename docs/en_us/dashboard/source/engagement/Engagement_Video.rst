.. _Engagement_Video:

#############################
Engagement with Course Videos
#############################

.. note:: At this time, data and reports for course videos are available for
  Open edX installations only.

Are learners watching the course videos? Do they watch some videos more than
others? Of those who watched a video, what percentage watched it to the end?
Do learners watch certain parts of the video more than once?

The video engagement data in edX Insights gives you information to gain
perspective on your learners' viewing patterns.

Video engagement data is updated every week for the period Monday at 00:00
UTC through Sunday at 23:59 UTC.

********************************************
Gaining Insight into Viewing Patterns
********************************************

EdX Insights delivers data about learner engagement with videos in a series of
charts and reports. Charts, metrics, and data are available for each of the
videos in your course. To access data about a specific video, you select the
section and subsection of the course that contain that video. When you make
these selections, edX Insights provides aggregated data about viewing patterns
for all videos in that part of the course outline.

For detailed information about the computations, see :ref:`Reference`.

*********************************************
Selecting the Section, Subsection, and Video
*********************************************

To access data about a video component, follow these steps.

#. Open edX Insights at insights.edx.org. A list of the courses for which you
   have the admin or staff role appears.

#. Select the course.

#. Select **How did students interact with course videos?**. Alternatively,
   select **Engagement** and then **Video**. A chart and a table of aggregated
   video data for the sections in your course appears. The chart only includes
   bars for sections that include at least one video component.

#. Select a section in your course that contains video components. A chart and
   a table of aggregated video data for each subsection in that section
   appears. The chart only includes bars for subsections that include
   at least one video component. 

#. Select a subsection. A chart and a table of aggregated video data for each
   unit in that subsection appears. The chart only includes bars for units
   that include at least one video component.

#. Select the unit that contains the video component. A chart, metrics, and a
   table of data for that video file appears.

For detailed information about the computations, see :ref:`Reference`.

*******************************************************
Analytics in Action: Interpreting Viewing Patterns
*******************************************************

A review of what learners in your course watch can lead to discoveries
about your videos and about your course.

* You can determine how many learners watch each video.

* You can determine how many learners watch the entire video, and where the
  other learners drop out.

* You can find video segments that learners watched more than once.

* You can discover what learners decide not to watch.

You can use this information to guide research on your video files and assess
where you might make changes.

=======================================================
Investigating Video Views for Sections and Subsections
=======================================================

To access data about a video, you select the section and subsection that
contain the video. When you make each of these selections, edX Insights
provides aggregated data of complete and incomplete video views.

In this chart of video views for the sections in a completed course, each bar
represents the number of views of all videos in a section. Each of the bars is
divided into the number of completed views in green and the number of
incomplete views in gray.

.. image:: ../images/video_sections.png
 :alt: A stacked bar chart showing varying levels of complete video watching.

Reviewing the aggregated data in this chart might lead you to investigate
several questions. You might want to understand why there are so many more
incomplete views in some of the sections than in others. Does your course have
numerous short videos in most of the sections, and fewer, comparatively long
videos in one or two of the other sections? Is there a difference in quality?
Could you have, accidentally or deliberately, included the same video file in
your course more than once?

When you select a section with a relatively low number of complete views,
another stacked bar chart appears for the subsections in that section. 

.. image:: ../images/video_subsections.png
 :alt: A stacked bar chart for three subsections. In one subsection, fewer
  than a third of the students who started videos finished watching them.

This chart helps you focus your investigation on the first subsection, in
which more than twice as many learners begin to view a video than complete the
viewing. After you select that subsection, the chart for video views in the
units appears. Once again, the aggregate data can help guide your
investigation into the disproportionate number of incomplete video views.

================================
Researching Replayed Segments
================================

When you review the chart for a video, you can see which five second segments
learners played more than once. The stacked area graph shows replays in darker
blue above plays by unique users.

When you see the graph for this video, you decide to investigate what exactly
happens at the 40 second mark.

.. image:: ../images/video_replays.png
 :alt: A chart showing a noticeable increase in the number of replays 40
  seconds into the video.

.. https://stage-insights.edx.org/courses/BerkeleyX/ColWri.2.2x/1T2015/engagement/videos/sections/i4x%3A//BerkeleyX/ColWri.2.2x/chapter/42e28dbf0b81488887be0f92a44484c9/subsections/i4x%3A//BerkeleyX/ColWri.2.2x/sequential/19a7ac548119487181e1f466cf48444c/modules/i4x%3A//BerkeleyX/ColWri.2.2x/video/ebe6682c6c3f424c9e59fff972ac19a4/timeline/

To find out what that segment of the video contains, you select **View Live**
to open the LMS to the unit that contains that video. In this example, a
single word is difficult to understand. Because the transcript for the video
is accurate, you might decide that no action is needed in this case.

In another video, the stacked area graph shows that learners replayed certain
segments of the video, particularly near the end, more often than others.

.. image:: ../images/video_frequent_replays.png
 :alt: A chart showing significant increases in the number of replays during
     the last three minutes of the video.

.. https://stage-insights.edx.org/courses/course-v1%3ACaltechX%2BEc1011x_2%2BT12015/engagement/videos/sections/block-v1%3ACaltechX%2BEc1011x_2%2BT12015%2Btype%40chapter%2Bblock%40d9e39345ddf744dd901cc9b290b72854/subsections/block-v1%3ACaltechX%2BEc1011x_2%2BT12015%2Btype%40sequential%2Bblock%40228af3c5dd49458393b568c52777618e/modules/block-v1%3ACaltechX%2BEc1011x_2%2BT12015%2Btype%40video%2Bblock%40aad61465c75f43d1ba5c8c8acb25a054/timeline/

After you review the video in the LMS, you might decide that the increased
number of replays was an indicator of the complexity of the material being
covered. You might decide to spend some extra time answering questions in the
discussion topic for that unit, or provide a course handout with additional
references on the material covered for learners who want them.

==========================================
Establishing an Engagement Baseline
==========================================

Week 1 of your course begins with a videotaped lecture that is about an hour
long. About two weeks after the course start date you use the video metrics
available in edX Insights to find that over 35,000 learners started playing
the video, and that almost 18,000 learners completed it.

You decide that this count of 18,000 will be a more meaningful baseline of
committed learners than the overall course enrollment count. As your course
progresses, you use the number of learners who completed the first video as
the basis for evaluating how many learners continue to engage with course
content.

===================================
What Are They Not Watching?
===================================

In addition to giving you information about how many learners are watching your
course videos, edX Insights can also help you investigate what, and when, they
choose not to watch.

When you see the graph in edX Insights for this video, you notice that there is
a temporary drop in the number of completed segment views near the beginning of
the video. This goes on for about a minute, and then the number recovers to the
previous level.

.. image:: ../images/video_skips.png
 :alt: A chart showing that the number of views completed the third minute of
     the video dropped, but then resumed  in the fourth minute.

.. https://stage-insights.edx.org/courses/HarvardX/CS50x3/2015/engagement/videos/sections/i4x%3A//HarvardX/CS50x3/chapter/b2f7d86728354866a2c4438e76c3ec55/subsections/i4x%3A//HarvardX/CS50x3/sequential/92f0ffe3349d430abd577474c4afb5e7/modules/i4x%3A//HarvardX/CS50x3/video/26006008b43e46ddb64dff7d24fbab5c/timeline/

This pattern indicates that learners chose to skip whatever was included in
that part of the video, but then they began playing the video again about a
minute further on.

In another video, the stacked area graph shows a steady decline in views and very little replay activity. 

.. image:: ../images/video_dropoff.png
 :alt: A chart showing that almost 30% of the viewers stopped watching during
     the first 30 seconds of a video, and only 35% were watching by the end.

.. https://stage-insights.edx.org/courses/ANUx/ANU-INDIA1x/1T2014/engagement/videos/sections/i4x%3A//ANUx/ANU-INDIA1x/chapter/a43ed3722f13420182f76b37459f94d1/subsections/i4x%3A//ANUx/ANU-INDIA1x/sequential/385b1e60985a481eb6cc3bb67f1a12c5/modules/i4x%3A//ANUx/ANU-INDIA1x/video/5aff579db6954184b2d1da9714390e87/timeline/

This pattern indicates that learners who began to play the video did not
continue to the end, and that they rarely chose to replay any of its segments.

The course teams might be curious to learn why learners chose to skip over part
of a video or to stop watching it completely. Analyzing the content of a video
with the objectivity that you gain from edX Insights can help you find content
that is not well matched to its audience. Perhaps you included an interview
that is pertinent for a residential student, but that your MOOC participants
find less interesting than other material. Or perhaps the video included
repetition that most of your learners did not need to grasp a concept.

Course teams that try to deduce the cause of viewing patterns like these might
not take any action for a currently running course. However, they might share
their deductions in an organizational "video best practices guide" for future
reference.
