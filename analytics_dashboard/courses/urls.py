# pylint: disable=no-value-for-parameter

from django.conf.urls import url, patterns, include

from courses import views

CONTENT_ID_PATTERN = r'(?P<content_id>[\.a-zA-Z0-9_+\/:-]+)'
COURSE_ID_PATTERN = r'(?P<course_id>[^/+]+[/+][^/+]+[/+][^/]+)'
PROBLEM_PART_ID_PATTERN = r'(?P<problem_part_id>[^/]+)'
ASSIGNMENT_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'assignment_id')
PROBLEM_ID_PATTERN = CONTENT_ID_PATTERN.replace('content_id', 'problem_id')

# pylint: disable=line-too-long
answer_distribution_regex = r'^performance/graded_content/assignments/{assignment_id}/problems/{problem_id}/parts/{part_id}/answer_distribution/$'.format(
    assignment_id=ASSIGNMENT_ID_PATTERN, problem_id=PROBLEM_ID_PATTERN, part_id=PROBLEM_PART_ID_PATTERN)

COURSE_URLS = patterns(
    '',
    # Course homepage. This should be the entry point for other applications linking to the course.
    url(r'^$', views.CourseHome.as_view(), name='home'),
    url(r'^enrollment/activity/$', views.EnrollmentActivityView.as_view(), name='enrollment_activity'),
    url(r'^enrollment/geography/$', views.EnrollmentGeographyView.as_view(), name='enrollment_geography'),
    url(r'^enrollment/demographics/age/$', views.EnrollmentDemographicsAgeView.as_view(),
        name='enrollment_demographics_age'),
    url(r'^enrollment/demographics/education/$', views.EnrollmentDemographicsEducationView.as_view(),
        name='enrollment_demographics_education'),
    url(r'^enrollment/demographics/gender/$', views.EnrollmentDemographicsGenderView.as_view(),
        name='enrollment_demographics_gender'),
    url(r'^engagement/content/$', views.EngagementContentView.as_view(), name='engagement_content'),

    url(r'^csv/enrollment/$', views.CourseEnrollmentCSV.as_view(), name='csv_enrollment'),
    url(r'^csv/enrollment_by_country/$', views.CourseEnrollmentByCountryCSV.as_view(),
        name='csv_enrollment_by_country'),
    url(r'^csv/enrollment_demographics_age/$', views.CourseEnrollmentDemographicsAgeCSV.as_view(),
        name='csv_enrollment_demographics_age'),
    url(r'^csv/enrollment_demographics_education/$', views.CourseEnrollmentDemographicsEducationCSV.as_view(),
        name='csv_enrollment_demographics_education'),
    url(r'^csv/enrollment_demographics_gender/$', views.CourseEnrollmentDemographicsGenderCSV.as_view(),
        name='csv_enrollment_demographics_gender'),
    url(r'^csv/engagement_activity_trend/$', views.CourseEngagementActivityTrendCSV.as_view(),
        name='csv_engagement_activity_trend'),
    url(r'^csv/performance/graded_content/problems/{}/answer_distribution/(?P<problem_part_id>[^/]+)/$'.format(
        CONTENT_ID_PATTERN),
        views.PerformanceAnswerDistributionCSV.as_view(), name='csv_performance_answer_distribution'),
    url(r'^performance/graded_content/$', views.PerformanceGradedContent.as_view(), name='performance_graded_content'),
    url(r'^performance/graded_content/(?P<assignment_type>\w+)/$', views.PerformanceGradedContentByType.as_view(),
        name='performance_graded_content_by_type'),
    url(answer_distribution_regex,
        views.PerformanceAnswerDistributionView.as_view(),
        name='performance_answer_distribution'),
    url(r'^performance/graded_content/assignments/{}/$'.format(ASSIGNMENT_ID_PATTERN),
        views.PerformanceAssignment.as_view(), name='performance_assignment'),
)

urlpatterns = patterns(
    '',
    url('^$', views.CourseIndex.as_view(), name='index'),
    url(r'^{}/'.format(COURSE_ID_PATTERN), include(COURSE_URLS))
)
