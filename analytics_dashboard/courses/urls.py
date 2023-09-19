from django.conf import settings
from django.urls import include, path, re_path

from analytics_dashboard.courses import views
from analytics_dashboard.courses.views import (
    course_summaries,
    csv,
    engagement,
    enrollment,
    performance,
)

CONTENT_ID_PATTERN = r'(?P<content_id>(?:i4x://?[^/]+/[^/]+/[^/]+/[^@]+(?:@[^/]+)?)|(?:[^/]+))'
PROBLEM_PART_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'problem_part_id')
ASSIGNMENT_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'assignment_id')
PROBLEM_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'problem_id')
SECTION_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'section_id')
SUBSECTION_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'subsection_id')
VIDEO_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'video_id')
PIPELINE_VIDEO_ID = r'(?P<pipeline_video_id>([^/+]+[/+][^/+]+[/+][^/]+)+[|]((?:i4x://?[^/]+/[^/]+/[^/]+' \
                    r'/[^@]+(?:@[^/]+)?)|(?:[^/]+)+))'
TAG_VALUE_ID_PATTERN = r'(?P<tag_value>[\w-]+)'

answer_distribution_regex = \
    r'^graded_content/assignments/{assignment_id}/problems/{problem_id}/parts/{part_id}/answer_distribution/$'.format(
        assignment_id=ASSIGNMENT_ID_PATTERN, problem_id=PROBLEM_ID_PATTERN, part_id=PROBLEM_PART_ID_PATTERN)

ungraded_answer_distribution_regex = \
    r'^ungraded_content/sections/{}/subsections/{}/problems/{}/parts/{}/answer_distribution/$'.format(
        SECTION_ID_PATTERN, SUBSECTION_ID_PATTERN, PROBLEM_ID_PATTERN, PROBLEM_PART_ID_PATTERN)

video_timeline_regex = \
    r'^videos/sections/{}/subsections/{}/modules/{}/timeline/$'.format(
        SECTION_ID_PATTERN, SUBSECTION_ID_PATTERN, VIDEO_ID_PATTERN)

ENROLLMENT_URLS = ([
    path('activity/', enrollment.EnrollmentActivityView.as_view(), name='activity'),
    path('geography/', enrollment.EnrollmentGeographyView.as_view(), name='geography'),
    path('demographics/age/', enrollment.EnrollmentDemographicsAgeView.as_view(), name='demographics_age'),
    path('demographics/education/', enrollment.EnrollmentDemographicsEducationView.as_view(),
         name='demographics_education'),
    path('demographics/gender/', enrollment.EnrollmentDemographicsGenderView.as_view(), name='demographics_gender'),
], 'enrollment')

ENGAGEMENT_URLS = ([
    path('content/', engagement.EngagementContentView.as_view(), name='content'),
    path('videos/', engagement.EngagementVideoCourse.as_view(), name='videos'),
    # ordering of the URLS is important for routing the the section, subsection, etc. correctly
    re_path(video_timeline_regex, engagement.EngagementVideoTimeline.as_view(), name='video_timeline'),
    re_path(fr'^videos/sections/{SECTION_ID_PATTERN}/subsections/{SUBSECTION_ID_PATTERN}/$',
            engagement.EngagementVideoSubsection.as_view(),
            name='video_subsection'),
    re_path(fr'^videos/sections/{SECTION_ID_PATTERN}/$',
            engagement.EngagementVideoSection.as_view(),
            name='video_section'),
], 'engagement')

PERFORMANCE_URLS = ([
    path('ungraded_content/', performance.PerformanceUngradedContent.as_view(), name='ungraded_content'),
    re_path(ungraded_answer_distribution_regex, performance.PerformanceUngradedAnswerDistribution.as_view(),
            name='ungraded_answer_distribution'),
    re_path(fr'^ungraded_content/sections/{SECTION_ID_PATTERN}/subsections/{SUBSECTION_ID_PATTERN}/$',
            performance.PerformanceUngradedSubsection.as_view(),
            name='ungraded_subsection'),
    re_path(fr'^ungraded_content/sections/{SECTION_ID_PATTERN}/$',
            performance.PerformanceUngradedSection.as_view(),
            name='ungraded_section'),
    path('graded_content/', performance.PerformanceGradedContent.as_view(), name='graded_content'),
    re_path(r'^graded_content/(?P<assignment_type>[\w-]+)/$',
            performance.PerformanceGradedContentByType.as_view(),
            name='graded_content_by_type'),
    re_path(answer_distribution_regex,
            performance.PerformanceAnswerDistributionView.as_view(),
            name='answer_distribution'),

    # This MUST come AFTER the answer distribution pattern; otherwise, the answer distribution pattern
    # will be interpreted as an assignment pattern.
    re_path(fr'^graded_content/assignments/{ASSIGNMENT_ID_PATTERN}/$',
            performance.PerformanceAssignment.as_view(),
            name='assignment'),
    path('learning_outcomes/',
         performance.PerformanceLearningOutcomesContent.as_view(),
         name='learning_outcomes'),
    re_path(fr'^learning_outcomes/{TAG_VALUE_ID_PATTERN}/$',
            performance.PerformanceLearningOutcomesSection.as_view(),
            name='learning_outcomes_section'),
    re_path(fr'^learning_outcomes/{TAG_VALUE_ID_PATTERN}/problems/{PROBLEM_ID_PATTERN}/$',
            performance.PerformanceLearningOutcomesAnswersDistribution.as_view(),
            name='learning_outcomes_answers_distribution'),
    re_path(r'^learning_outcomes/{}/problems/{}/{}/$'.format(
        TAG_VALUE_ID_PATTERN, PROBLEM_ID_PATTERN, PROBLEM_PART_ID_PATTERN),
        performance.PerformanceLearningOutcomesAnswersDistribution.as_view(),
        name='learning_outcomes_answers_distribution_with_part'),
], 'performance')

CSV_URLS = ([
    path('enrollment/', csv.CourseEnrollmentCSV.as_view(), name='enrollment'),
    path('enrollment/geography/', csv.CourseEnrollmentByCountryCSV.as_view(), name='enrollment_geography'),
    path('enrollment/demographics/age/',
         csv.CourseEnrollmentDemographicsAgeCSV.as_view(),
         name='enrollment_demographics_age'),
    path('enrollment/demographics/education/',
         csv.CourseEnrollmentDemographicsEducationCSV.as_view(),
         name='enrollment_demographics_education'),
    path('enrollment/demographics/gender/',
         csv.CourseEnrollmentDemographicsGenderCSV.as_view(),
         name='enrollment_demographics_gender'),
    path('engagement/activity_trend/',
         csv.CourseEngagementActivityTrendCSV.as_view(),
         name='engagement_activity_trend'),
    re_path(fr'^engagement/videos/{PIPELINE_VIDEO_ID}/$',
            csv.CourseEngagementVideoTimelineCSV.as_view(),
            name='engagement_video_timeline'),
    re_path(r'^performance/graded_content/problems/{}/answer_distribution/{}/$'.format(
        CONTENT_ID_PATTERN,
        PROBLEM_PART_ID_PATTERN),
        csv.PerformanceAnswerDistributionCSV.as_view(),
        name='performance_answer_distribution'),
    re_path(r'problem_responses/', csv.PerformanceProblemResponseCSV.as_view(), name='performance_problem_responses')
], 'csv')

COURSE_URLS = [
    # Course homepage. This should be the entry point for other applications linking to the course.
    path('', views.CourseHome.as_view(), name='home'),
    path('enrollment/', include(ENROLLMENT_URLS)),
    path('engagement/', include(ENGAGEMENT_URLS)),
    path('performance/', include(PERFORMANCE_URLS)),
    path('csv/', include(CSV_URLS)),
]

app_name = 'courses'
urlpatterns = [
    path('', course_summaries.CourseIndex.as_view(), name='index'),
    re_path(fr'^{settings.COURSE_ID_PATTERN}/', include(COURSE_URLS)),
    path('csv/course_list/', course_summaries.CourseIndexCSV.as_view(), name='index_csv')
]
