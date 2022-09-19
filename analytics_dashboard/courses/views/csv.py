import datetime
import logging
import urllib

from analyticsclient.client import Client
from analyticsclient.constants import data_formats, demographics
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone

from analytics_dashboard.courses.presenters.performance import CourseReportDownloadPresenter
from analytics_dashboard.courses.views import CourseView, AnalyticsV0Mixin, AnalyticsV1Mixin

logger = logging.getLogger(__name__)


class CSVResponseMixin:
    """An abstract class for defining mixins that will make a view return data in CSV format."""
    csv_filename_suffix = None

    # pylint: disable=unused-argument
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(self.get_data(), content_type='text/csv', **response_kwargs)
        response['Content-Disposition'] = f'attachment; filename="{self._get_filename()}"'
        return response

    def get_data(self):
        raise NotImplementedError

    @property
    def csv_identifier(self):
        """Unique string to identify an instance of the CSV output. Prefix of the CSV filename.

        Type of CSV output is defined by csv_filename_suffix.
        """
        raise NotImplementedError

    def _get_filename(self):
        """Concatenates the unique csv_identifier with the general csv_filename_suffix for this class."""
        filename = f'{self.csv_identifier}--{self.csv_filename_suffix}.csv'
        return urllib.parse.quote(filename)


# pylint: disable=W0223
class CourseCSVResponseMixin(CSVResponseMixin):
    """A CSVResponseMixin that implements csv_identifier to be the view's course id."""
    @property
    def csv_identifier(self):
        course_key = self.course_key
        return '-'.join([course_key.org, course_key.course, course_key.run])


# pylint: disable=W0223
class DatetimeCSVResponseMixin(CSVResponseMixin):
    """A CSVResponseMixin that implements csv_identifier to be the current time in ISO format."""
    @property
    def csv_identifier(self):
        return timezone.now().replace(microsecond=0).isoformat()


class CourseEnrollmentDemographicsAgeCSV(AnalyticsV0Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'enrollment-by-birth-year'

    def get_data(self):
        return self.course.enrollment(demographics.BIRTH_YEAR, data_format=data_formats.CSV)


class CourseEnrollmentDemographicsEducationCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'enrollment-by-education'

    def get_data(self):
        return self.course.enrollment(demographics.EDUCATION, data_format=data_formats.CSV)


class CourseEnrollmentDemographicsGenderCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'enrollment-by-gender'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.enrollment(demographics.GENDER, end_date=end_date, data_format=data_formats.CSV)


class CourseEnrollmentByCountryCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'enrollment-location'

    def get_data(self):
        return self.course.enrollment(demographics.LOCATION, data_format=data_formats.CSV)


class CourseEnrollmentCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'enrollment'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.enrollment('mode', data_format=data_formats.CSV, end_date=end_date)


class CourseEngagementActivityTrendCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'engagement-activity'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.activity(data_format=data_formats.CSV, end_date=end_date)


class CourseEngagementVideoTimelineCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'engagement-video-timeline'

    def get_data(self):
        modules = self.analytics_client.modules(self.course_id, self.kwargs['pipeline_video_id'])
        return modules.video_timeline(data_format=data_formats.CSV)


class PerformanceAnswerDistributionCSV(AnalyticsV1Mixin, CourseCSVResponseMixin, CourseView):
    csv_filename_suffix = 'performance-answer-distribution'

    def get_data(self):
        modules = self.analytics_client.modules(self.course_id, self.kwargs['content_id'])
        return modules.answer_distribution(data_format=data_formats.CSV)


class PerformanceProblemResponseCSV(AnalyticsV1Mixin, CourseView):
    """
    Query the Data API to get a temporary secure download URL, and redirect to that.
    """
    def render_to_response(self, context, **response_kwargs):
        presenter = CourseReportDownloadPresenter(self.course_id, self.analytics_client)
        data = presenter.get_report_info(CourseReportDownloadPresenter.PROBLEM_RESPONSES)
        return HttpResponseRedirect(data['download_url'], **response_kwargs)
