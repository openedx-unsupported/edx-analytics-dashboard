# pylint: disable=no-value-for-parameter

from django.conf.urls import url, patterns, include

from courses import views

COURSE_ID_PATTERN = r'(?P<course_id>[^/+]+[/+][^/+]+[/+][^/]+)'
CONTENT_ID_PATTERN = r'(?P<content_id>[\.a-zA-Z0-9_+\/:-]+)'

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
    url(r'^performance/graded_content/problems/{}/answerdistribution/(?P<problem_part_id>[^/]+)/$'.format(
        CONTENT_ID_PATTERN),
        views.PerformanceAnswerDistributionView.as_view(), name='performance_answerdistribution'),
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
    url(r'^csv/performance/graded_content/problems/{}/answerdistribution/(?P<problem_part_id>[^/]+)/$'.format(
        CONTENT_ID_PATTERN),
        views.PerformanceAnswerDistributionCSV.as_view(), name='csv_performance_answerdistribution'),
)

urlpatterns = patterns(
    '',
    url('^$', views.CourseIndex.as_view(), name='index'),
    url(r'^{}/'.format(COURSE_ID_PATTERN), include(COURSE_URLS))
)
