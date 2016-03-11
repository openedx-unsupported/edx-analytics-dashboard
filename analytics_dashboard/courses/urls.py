# pylint: disable=no-value-for-parameter
from django.conf import settings
from django.conf.urls import url, patterns, include

from courses import views
from courses.views import enrollment, engagement, performance, csv, learners

CONTENT_ID_PATTERN = r'(?P<content_id>(?:i4x://?[^/]+/[^/]+/[^/]+/[^@]+(?:@[^/]+)?)|(?:[^/]+))'
PROBLEM_PART_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'problem_part_id')
ASSIGNMENT_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'assignment_id')
PROBLEM_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'problem_id')
SECTION_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'section_id')
SUBSECTION_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'subsection_id')
VIDEO_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'video_id')
PIPELINE_VIDEO_ID = r'(?P<pipeline_video_id>([^/+]+[/+][^/+]+[/+][^/]+)+[|]((?:i4x://?[^/]+/[^/]+/[^/]+' \
                    r'/[^@]+(?:@[^/]+)?)|(?:[^/]+)+))'

answer_distribution_regex = \
    r'^graded_content/assignments/{assignment_id}/problems/{problem_id}/parts/{part_id}/answer_distribution/$'.format(
        assignment_id=ASSIGNMENT_ID_PATTERN, problem_id=PROBLEM_ID_PATTERN, part_id=PROBLEM_PART_ID_PATTERN)

ungraded_answer_distribution_regex = \
    r'^ungraded_content/sections/{}/subsections/{}/problems/{}/parts/{}/answer_distribution/$'.format(
        SECTION_ID_PATTERN, SUBSECTION_ID_PATTERN, PROBLEM_ID_PATTERN, PROBLEM_PART_ID_PATTERN)

video_timeline_regex = \
    r'^videos/sections/{}/subsections/{}/modules/{}/timeline/$'.format(
        SECTION_ID_PATTERN, SUBSECTION_ID_PATTERN, VIDEO_ID_PATTERN)

ENROLLMENT_URLS = patterns(
    '',
    url(r'^activity/$', enrollment.EnrollmentActivityView.as_view(), name='activity'),
    url(r'^geography/$', enrollment.EnrollmentGeographyView.as_view(), name='geography'),
    url(r'^demographics/age/$', enrollment.EnrollmentDemographicsAgeView.as_view(), name='demographics_age'),
    url(r'^demographics/education/$', enrollment.EnrollmentDemographicsEducationView.as_view(),
        name='demographics_education'),
    url(r'^demographics/gender/$', enrollment.EnrollmentDemographicsGenderView.as_view(), name='demographics_gender'),
)

ENGAGEMENT_URLS = patterns(
    '',
    url(r'^content/$', engagement.EngagementContentView.as_view(), name='content'),
    url(r'^videos/$', engagement.EngagementVideoCourse.as_view(), name='videos'),
    # ordering of the URLS is important for routing the the section, subsection, etc. correctly
    url(video_timeline_regex, engagement.EngagementVideoTimeline.as_view(), name='video_timeline'),
    url(r'^videos/sections/{}/subsections/{}/$'.format(SECTION_ID_PATTERN, SUBSECTION_ID_PATTERN),
        engagement.EngagementVideoSubsection.as_view(),
        name='video_subsection'),
    url(r'^videos/sections/{}/$'.format(SECTION_ID_PATTERN),
        engagement.EngagementVideoSection.as_view(),
        name='video_section'),
)

PERFORMANCE_URLS = patterns(
    '',
    url(r'^ungraded_content/$', performance.PerformanceUngradedContent.as_view(), name='ungraded_content'),
    url(ungraded_answer_distribution_regex, performance.PerformanceUngradedAnswerDistribution.as_view(),
        name='ungraded_answer_distribution'),
    url(r'^ungraded_content/sections/{}/subsections/{}/$'.format(SECTION_ID_PATTERN, SUBSECTION_ID_PATTERN),
        performance.PerformanceUngradedSubsection.as_view(),
        name='ungraded_subsection'),
    url(r'^ungraded_content/sections/{}/$'.format(SECTION_ID_PATTERN),
        performance.PerformanceUngradedSection.as_view(),
        name='ungraded_section'),
    url(r'^graded_content/$', performance.PerformanceGradedContent.as_view(), name='graded_content'),
    url(r'^graded_content/(?P<assignment_type>[\w-]+)/$',
        performance.PerformanceGradedContentByType.as_view(),
        name='graded_content_by_type'),
    url(answer_distribution_regex, performance.PerformanceAnswerDistributionView.as_view(), name='answer_distribution'),

    # This MUST come AFTER the answer distribution pattern; otherwise, the answer distribution pattern
    # will be interpreted as an assignment pattern.
    url(r'^graded_content/assignments/{}/$'.format(ASSIGNMENT_ID_PATTERN),
        performance.PerformanceAssignment.as_view(),
        name='assignment'),
)

CSV_URLS = patterns(
    '',
    url(r'^enrollment/$', csv.CourseEnrollmentCSV.as_view(), name='enrollment'),
    url(r'^enrollment/geography/$', csv.CourseEnrollmentByCountryCSV.as_view(), name='enrollment_geography'),
    url(r'^enrollment/demographics/age/$',
        csv.CourseEnrollmentDemographicsAgeCSV.as_view(),
        name='enrollment_demographics_age'),
    url(r'^enrollment/demographics/education/$',
        csv.CourseEnrollmentDemographicsEducationCSV.as_view(),
        name='enrollment_demographics_education'),
    url(r'^enrollment/demographics/gender/$',
        csv.CourseEnrollmentDemographicsGenderCSV.as_view(),
        name='enrollment_demographics_gender'),
    url(r'^engagement/activity_trend/$',
        csv.CourseEngagementActivityTrendCSV.as_view(),
        name='engagement_activity_trend'),
    url(r'^engagement/videos/{}/$'.format(PIPELINE_VIDEO_ID),
        csv.CourseEngagementVideoTimelineCSV.as_view(),
        name='engagement_video_timeline'),
    url(r'^performance/graded_content/problems/{}/answer_distribution/{}/$'.format(CONTENT_ID_PATTERN,
                                                                                   PROBLEM_PART_ID_PATTERN),
        csv.PerformanceAnswerDistributionCSV.as_view(),
        name='performance_answer_distribution'),
)

LEARNER_URLS = patterns(
    '',
    url(r'^$', learners.LearnersView.as_view(), name='learners'),
)

COURSE_URLS = patterns(
    '',
    # Course homepage. This should be the entry point for other applications linking to the course.
    url(r'^$', views.CourseHome.as_view(), name='home'),
    url(r'^enrollment/', include(ENROLLMENT_URLS, namespace='enrollment')),
    url(r'^engagement/', include(ENGAGEMENT_URLS, namespace='engagement')),
    url(r'^performance/', include(PERFORMANCE_URLS, namespace='performance')),
    url(r'^csv/', include(CSV_URLS, namespace='csv')),
    url(r'^learners/', include(LEARNER_URLS, namespace='learners')),
)

urlpatterns = patterns(
    '',
    url('^$', views.CourseIndex.as_view(), name='index'),
    url(r'^{}/'.format(settings.COURSE_ID_PATTERN), include(COURSE_URLS))
)
