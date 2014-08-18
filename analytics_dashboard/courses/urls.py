# pylint: disable=no-value-for-parameter

from django.conf.urls import url, patterns

from courses import views
import re

COURSE_URLS = [
    ('enrollment/activity', views.EnrollmentActivityView.as_view()),
    ('enrollment/geography', views.EnrollmentGeographyView.as_view()),
    ('engagement/content', views.EngagementContentView.as_view()),
    ('performance', views.PerformanceView.as_view()),
    ('overview', views.OverviewView.as_view()),
    ('csv/enrollment', views.CourseEnrollmentCSV.as_view()),
    ('csv/enrollment_by_country', views.CourseEnrollmentByCountryCSV.as_view()),
]

COURSE_ID_REGEX = r'^(?P<course_id>(\w+/){2}\w+)'
TRAILING_SLASH_REGEX = r'/$'

urlpatterns = patterns(
    '',
    # Course homepage. This should be the entry point for other applications linking to the course.
    url(COURSE_ID_REGEX + TRAILING_SLASH_REGEX, views.CourseHome.as_view(), name='home')
)


def generate_regex(path):
    return COURSE_ID_REGEX + re.escape('/' + path) + TRAILING_SLASH_REGEX


for name, view in COURSE_URLS:
    # Create a new URL pattern. Slashes are valid for paths, but not names. Replace any forward slashes
    # with an underscore.
    urlpatterns += patterns('', url(generate_regex(name), view, name=name.replace('/', '_')))
