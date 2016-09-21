import datetime
import logging
import urllib

from django.http import HttpResponse, HttpResponseRedirect

from analyticsclient.constants import data_format, demographic
from analyticsclient.client import Client

from courses.presenters.performance import CourseReportDownloadPresenter
from courses.views import CourseView


logger = logging.getLogger(__name__)


class CSVResponseMixin(object):
    csv_filename_suffix = None

    # pylint: disable=unused-argument
    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(self.get_data(), content_type='text/csv', **response_kwargs)
        response['Content-Disposition'] = u'attachment; filename="{0}"'.format(self._get_filename())
        return response

    def get_data(self):
        raise NotImplementedError

    def _get_filename(self):
        course_key = self.course_key
        course_id = '-'.join([course_key.org, course_key.course, course_key.run])
        filename = u'{0}--{1}.csv'.format(course_id, self.csv_filename_suffix)
        return urllib.quote(filename)


class CourseEnrollmentDemographicsAgeCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-by-birth-year'

    def get_data(self):
        return self.course.enrollment(demographic.BIRTH_YEAR, data_format=data_format.CSV),


class CourseEnrollmentDemographicsEducationCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-by-education'

    def get_data(self):
        return self.course.enrollment(demographic.EDUCATION, data_format=data_format.CSV),


class CourseEnrollmentDemographicsGenderCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-by-gender'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.enrollment(demographic.GENDER, end_date=end_date, data_format=data_format.CSV),


class CourseEnrollmentByCountryCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment-location'

    def get_data(self):
        return self.course.enrollment(demographic.LOCATION, data_format=data_format.CSV)


class CourseEnrollmentCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'enrollment'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.enrollment('mode', data_format=data_format.CSV, end_date=end_date)


class CourseEngagementActivityTrendCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'engagement-activity'

    def get_data(self):
        end_date = datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)
        return self.course.activity(data_format=data_format.CSV, end_date=end_date)


class CourseEngagementVideoTimelineCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'engagement-video-timeline'

    def get_data(self):
        modules = self.client.modules(self.course_id, self.kwargs['pipeline_video_id'])
        return modules.video_timeline(data_format=data_format.CSV)


class PerformanceAnswerDistributionCSV(CSVResponseMixin, CourseView):
    csv_filename_suffix = u'performance-answer-distribution'

    def get_data(self):
        modules = self.client.modules(self.course_id, self.kwargs['content_id'])
        return modules.answer_distribution(data_format=data_format.CSV)


class PerformanceProblemResponseCSV(CourseView):
    """
    Query the Data API to get a temporary secure download URL, and redirect to that.
    """
    # pylint: disable=unused-argument
    def render_to_response(self, context, **response_kwargs):
        presenter = CourseReportDownloadPresenter(self.course_id)
        data = presenter.get_report_info(CourseReportDownloadPresenter.PROBLEM_RESPONSES)
        return HttpResponseRedirect(data['download_url'], **response_kwargs)
