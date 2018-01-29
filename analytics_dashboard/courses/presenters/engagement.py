import datetime
import logging
import math

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from waffle import switch_is_active

from analyticsclient.client import Client
import analyticsclient.constants.activity_type as AT
from analyticsclient.exceptions import NotFoundError

from core.templatetags.dashboard_extras import metric_percentage
from courses import utils
from courses.exceptions import NoVideosError
from courses.presenters import (CoursePresenter, CourseAPIPresenterMixin)


logger = logging.getLogger(__name__)


class CourseEngagementActivityPresenter(CoursePresenter):
    """
    Presenter for the engagement activity page.
    """

    def get_activity_types(self):
        activities = [AT.ANY, AT.PLAYED_VIDEO, AT.ATTEMPTED_PROBLEM]

        # Include forum activity only if feature is enabled.
        if switch_is_active('show_engagement_forum_activity'):
            activities.append(AT.POSTED_FORUM)

        return activities

    def _build_trend_week(self, trend_types, week_ending, api_trend):
        trend_week = {'weekEnding': week_ending.isoformat()}
        for trend_type in trend_types:
            if trend_type in api_trend:
                trend_week[trend_type] = api_trend[trend_type] or 0
            else:
                trend_week[trend_type] = 0
        return trend_week

    def _build_trend(self, api_trends):
        """
        Format activity trends for specified date range and return results with
        zeros filled in for all activities.
        """
        trend_types = self.get_activity_types()
        trends = []

        # add zeros for the week prior if we only have a single point (prevents just a single point in the chart)
        if len(api_trends) == 1:
            interval_end = self.parse_api_datetime(api_trends[0]['interval_end'])
            week_ending = interval_end.date() - datetime.timedelta(days=8)
            trends.append(self._build_trend_week(trend_types, week_ending, {}))

        # fill in gaps in activity with zero for display (api doesn't return
        # the field if no data exists for it, so we fill in the zeros here)
        for datum in api_trends:
            # convert end of interval to ending day of week
            interval_end = self.parse_api_datetime(datum['interval_end'])
            week_ending = interval_end.date() - datetime.timedelta(days=1)
            trends.append(self._build_trend_week(trend_types, week_ending, datum))

        return trends

    def _build_summary(self, api_trends):
        """
        Format all summary numbers and week ending time.
        """

        most_recent = api_trends[-1]
        summary = {
            'last_updated': self.parse_api_datetime(most_recent['created'])
        }

        # Fill in gaps in the summary if no data found so we can display a proper message
        activity_types = self.get_activity_types()
        for activity_type in activity_types:
            if activity_type in most_recent:
                summary[activity_type] = most_recent[activity_type]
            else:
                summary[activity_type] = None

        return summary

    def _annotate_with_enrollment(self, summary, trends, enrollment_data):
        """
        Add weekly enrollment data to the summary and trends so we can display stats as a
        percentage of the total enrollment at the time.
        """
        # Approximate the weekly enrollment using the last day of each week:
        enrollment_by_day = {datum['date']: datum['count'] for datum in enrollment_data}
        has_enrollment_data = any(enrollment_by_day.get(week['weekEnding']) for week in trends)
        if not has_enrollment_data:
            return
        for week in trends:
            week['enrollment'] = enrollment_by_day.get(week['weekEnding'])
            num_active = week.get('any', 0)
            if num_active == 0:
                week['active_percent'] = 0
            elif week['enrollment']:
                week['active_percent'] = num_active / float(week['enrollment'])
            else:
                week['active_percent'] = None  # Avoid divide-by-zero but add an entry for this column so it appears

        # Find the latest weekEnding in the trends that we have enrollment data for.
        # (should usually be trends[-1] unless the enrollment data somehow got behind)
        summary_enrollment = None
        trends_step_back = 1
        while not summary_enrollment:
            if trends_step_back > len(trends):
                # No enrollment data for any of the dates in the activity trend data.
                # This should never be executed because of the has_enrollment_data check above.
                return
            most_recent = trends[-trends_step_back]
            summary_enrollment = enrollment_by_day.get(most_recent['weekEnding'])
            trends_step_back += 1

        if summary_enrollment:
            for key in self.get_activity_types():
                if summary.get(key):
                    # Translators: '{percentage}' in as a placeholder for the percentage value.
                    percent_str = _("{percentage} of current learners")
                    summary[key + '_percent_str'] = percent_str.format(
                        percentage=metric_percentage(summary[key] / float(summary_enrollment))
                    )
                elif key in summary:
                    summary[key + '_percent_str'] = '--'

    def get_summary_and_trend_data(self):
        """
        Retrieve recent summary and all historical trend data.
        """
        end_date = datetime.datetime.utcnow().strftime(Client.DATETIME_FORMAT)
        api_trends = self.course.activity(start_date=None, end_date=end_date)
        summary = self._build_summary(api_trends)
        trends = self._build_trend(api_trends)
        if trends:
            enrollment_data = self.course.enrollment(start_date=None, end_date=end_date)
            self._annotate_with_enrollment(summary, trends, enrollment_data)
        return summary, trends


class CourseEngagementVideoPresenter(CourseAPIPresenterMixin, CoursePresenter):

    def blocks_have_data(self, videos):
        if videos:
            for video in videos:
                if video['users_at_start'] > 0 or video['users_at_end'] > 0:
                    return True
        return False

    @property
    def section_type_template(self):
        return u'video_sections_{}_{}'

    @property
    def all_sections_key(self):
        return u'video_sections'

    @property
    def module_type(self):
        return 'video'

    def fetch_course_module_data(self):
        # Get the videos from the API.  Use course_module_data() for cached data.
        try:
            videos = self.client.courses(self.course_id).videos()
        except NotFoundError:
            raise NoVideosError(course_id=self.course_id)
        return videos

    def attach_computed_data(self, video):
        # Change the id key name
        if 'encoded_module_id' in video:
            video['id'] = video.pop('encoded_module_id')

        total = max([video['users_at_start'], video['users_at_end']])
        start_only_users = max(video['users_at_start'] - video['users_at_end'], 0)
        video.update({
            'end_percent': utils.math.calculate_percent(video['users_at_end'], total),
            'start_only_users': start_only_users,
            'start_only_percent': utils.math.calculate_percent(start_only_users, total),
        })

    def video_has_data(self, video_or_data):
        """
        Return True if and only if `video_or_data` represents a video that has been viewed.

        `video_or_data` is either a video block annotated with data or the data itself.
        """
        return video_or_data.get('users_at_start', 0) > 0 or video_or_data.get('users_at_end', 0) > 0

    def attach_aggregated_data_to_parent(self, index, parent, url_func=None):
        children = parent['children']
        total_start_users = sum(child.get('users_at_start', 0) for child in children)
        total_end_users = sum(child.get('users_at_end', 0) for child in children)
        parent.update({
            'users_at_start': total_start_users,
            'users_at_end': total_end_users,
            'index': index + 1,
            'average_start_only_users': 0,
            'average_users_at_end': 0,
        })

        # calculates the percentages too
        self.attach_computed_data(parent)

        has_views = any(self.video_has_data(video) for video in children)

        if has_views and parent['num_modules']:
            num_modules = float(parent['num_modules'])
            parent.update({
                'average_start_only_users': parent['start_only_users'] / num_modules,
                'average_users_at_end': total_end_users / num_modules,
            })

        # including the URL enables navigation to child pages
        if url_func > 0 and has_views:
            parent['url'] = url_func(parent)

    def build_section_url(self, section):
        return reverse('courses:engagement:video_section', kwargs={'course_id': self.course_id,
                                                                   'section_id': section['id']})

    def build_subsection_url_func(self, section_id):
        """
        Returns a function for creating the subsection URL.
        """
        # Using closures to keep the section ID available
        def subsection_url(subsection):
            return reverse('courses:engagement:video_subsection',
                           kwargs={'course_id': self.course_id,
                                   'section_id': section_id,
                                   'subsection_id': subsection['id']})
        return subsection_url

    def build_module_url_func(self, section_id):
        def build_url(parent, video):
            return reverse('courses:engagement:video_timeline',
                           kwargs={
                               'course_id': self.course_id,
                               'section_id': section_id,
                               'subsection_id': parent['id'],
                               'video_id': video['id']
                           })

        return build_url

    def post_process_adding_data_to_blocks(self, data, parent_block, child_block, url_func=None):
        if url_func and self.video_has_data(data):
            data['url'] = url_func(parent_block, child_block)

    @property
    def default_block_data(self):
        return {
            'users_at_start': 0,
            'users_at_end': 0,
            'start_only_users': 0,
            'start_only_percent': 0,
            'end_percent': 0
        }

    def module_id_to_data_id(self, module):
        """
        The data api only has the encoded module ID.  This converts the course structure ID
        to the encoded form.
        """
        return utils.get_encoded_module_id(module['id'])

    def get_video_timeline(self, video_module):
        """ Returns the video timeline with gaps in the beginning and end filled in with zeros. """
        api_response = self.client.modules(self.course_id, video_module['pipeline_video_id']).video_timeline()
        segment_length = video_module['segment_length']
        video_duration = video_module['duration']
        api_response = self._fill_video_timeline_gaps(api_response, self._calculate_total_video_segments(
            segment_length, video_duration))
        return self._build_video_timeline(api_response, segment_length, video_duration)

    def _calculate_total_video_segments(self, segment_length, video_duration=None):
        """ Return the total number of segments based on video duration or None if duration not specified. """
        total_segments = None
        if video_duration:
            total_segments = int(math.floor(video_duration/segment_length))
        return total_segments

    def _fill_video_timeline_gaps(self, api_response, segment_total=None):
        # fill any gaps at the beginning and between segments
        gaps = []
        expected_next_segment_index = 0
        for segment in api_response:
            current_segment_index = segment['segment']
            if current_segment_index > expected_next_segment_index:
                for i in range(expected_next_segment_index, current_segment_index):
                    gaps.append(self._get_default_video_timeline_segment(i))
            expected_next_segment_index = current_segment_index + 1
        api_response.extend(gaps)
        api_response = sorted(api_response, key=lambda segment: segment['segment'])

        # fill in the end of the timeline if needed
        if segment_total and len(api_response) > 1:
            next_segment = api_response[-1]['segment'] + 1
            for i in range(next_segment, segment_total + 1):
                api_response.append(self._get_default_video_timeline_segment(i))

        return api_response

    def _get_default_video_timeline_segment(self, segment_index):
        return {
            'num_users': 0,
            'num_views': 0,
            'segment': segment_index
        }

    def _build_video_timeline(self, api_response, segment_length, video_duration=None):
        """ Adds the replays, segment start time, and clips the final video time point if needed. """
        for segment in api_response:
            segment.update({
                'num_replays': segment['num_views'] - segment['num_users'],
                'start_time': segment['segment'] * segment_length,
            })

        # add a final data point at the video duration so that it doesn't look shorter than it actually is
        if video_duration and len(api_response) > 1:
            last_segment = api_response[-1].copy()
            last_segment.update({
                'start_time': video_duration,
                'segment': last_segment['segment'] + 1
            })
            api_response.append(last_segment)

        return api_response
