# pylint: disable=no-value-for-parameter

from django.conf.urls import url, patterns

from courses import views

COURSE_URLS = [
    ('enrollment/activity', views.EnrollmentActivityView.as_view()),
    ('enrollment/geography', views.EnrollmentGeographyView.as_view()),
    ('enrollment/demographics/age', views.EnrollmentDemographicsAgeView.as_view()),
    ('enrollment/demographics/education', views.EnrollmentDemographicsEducationView.as_view()),
    ('enrollment/demographics/gender', views.EnrollmentDemographicsGenderView.as_view()),
    ('engagement/content', views.EngagementContentView.as_view()),
    ('csv/enrollment', views.CourseEnrollmentCSV.as_view()),
    ('csv/enrollment_by_country', views.CourseEnrollmentByCountryCSV.as_view()),
    ('csv/enrollment_demographics_age', views.CourseEnrollmentDemographicsAgeCSV.as_view()),
    ('csv/enrollment_demographics_education', views.CourseEnrollmentDemographicsEducationCSV.as_view()),
    ('csv/enrollment_demographics_gender', views.CourseEnrollmentDemographicsGenderCSV.as_view()),
    ('csv/engagement_activity_trend', views.CourseEngagementActivityTrendCSV.as_view()),
    ('performance/graded_content', views.PerformanceGradedContent.as_view()),
]

COURSE_ID_PATTERN = r'(?P<course_id>[^/+]+[/+][^/+]+[/+][^/]+)'

urlpatterns = patterns(
    '',
    url('^$', views.CourseIndex.as_view(), name='index'),

    # Course homepage. This should be the entry point for other applications linking to the course.
    url(r'^{0}/$'.format(COURSE_ID_PATTERN), views.CourseHome.as_view(), name='home')
)


def generate_regex(path):
    return r'^{0}/{1}/$'.format(COURSE_ID_PATTERN, path)


for name, view in COURSE_URLS:
    # Create a new URL pattern. Slashes are valid for paths, but not names. Replace any forward slashes
    # with an underscore.
    urlpatterns += patterns('', url(generate_regex(name), view, name=name.replace('/', '_')))
