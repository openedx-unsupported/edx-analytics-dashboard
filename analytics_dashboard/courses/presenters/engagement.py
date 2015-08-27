# -*- coding: utf-8 -*-
from collections import defaultdict
import datetime
import math
from django.core.urlresolvers import reverse
import logging
from waffle import switch_is_active

from opaque_keys.edx.keys import UsageKey
from analyticsclient.client import Client
import analyticsclient.constants.activity_type as AT
import analyticsclient.constants.typology as TYPOLOGY
from analyticsclient.exceptions import NotFoundError

from courses import utils
from courses.exceptions import NoVideosError
from courses.presenters import (BasePresenter, SimpleCourseAPIPresenterMixin, CourseAPIPresenterMixin)


logger = logging.getLogger(__name__)


class CourseEngagementActivityPresenter(BasePresenter):
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

    def get_summary_and_trend_data(self):
        """
        Retrieve recent summary and all historical trend data.
        """
        # setting the end date (exclusive) to the next day retrieves data as soon as it's available
        end_date = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime(Client.DATE_FORMAT)
        api_trends = self.course.activity(start_date=None, end_date=end_date)
        summary = self._build_summary(api_trends)
        trends = self._build_trend(api_trends)
        return summary, trends


class CourseEngagementTypologyPresenter(SimpleCourseAPIPresenterMixin, BasePresenter):
    """
    Present the typology data that categorizes students into types per course section
    """
    def get_data(self):
        """
        Retrieve and present the available typology data for this course.

        Input is somewhat raw data from the API, like:
            [
                {"chapter_id": "week3", "video_type": 0, "problem_type": 1, "num_users": 2180, "created": datetime(…)},
                {"chapter_id": "week3", "video_type": 2, "problem_type": 1, "num_users": 1284, "created": datetime(…)},
                ⋮
            ]
        Output is grouped by section, ordered, and annotated with section names:
            [
                {
                    "id": "week3",
                    "index": 3,
                    "name": "Week 3",
                    "all_v_all_p": 3827, "all_v_all_p_fraction": 0.32,
                    "some_v_all_p": 3123, "some_v_all_p_fraction": 0.12,
                    "no_v_all_p": 1821, "no_v_all_p_fraction": 0.27,
                    "all_v_some_p": 1284, "all_v_some_p_fraction": 0.08,
                    "some_v_some_p": 542, "some_v_some_p_fraction": 0.18,
                    "no_v_some_p": 2180, "no_v_some_p_fraction": 0.07,
                    "all_v_no_p": 200, "all_v_no_p_fraction": 0.005,
                    "some_v_no_p": 365, "some_v_no_p_fraction": 0.00,
                },
                ⋮
            ]
        """
        raw_typology_data = self.course.typology()  # The raw data from the API (example in docstring above)

        def default_section_data():
            """ Factory for the info structure we want to describe each section """
            return {
                "index": 0,
                "name": "",
                "all_v_all_p": 0,  # Number of students who did "all videos, all problems"
                "some_v_all_p": 0,  # Number who did "some videos, all problems"
                "no_v_all_p": 0,  # etc.
                "all_v_some_p": 0,
                "some_v_some_p": 0,
                "no_v_some_p": 0,
                "all_v_no_p": 0,
                "some_v_no_p": 0,
                # There is no entry for "No videos, no problems" because we necessarily have no data about those users
            }

        # We build our data in data_by_section. The keys of this dict are block IDs like "week1"
        data_by_section = defaultdict(default_section_data)
        friendly_keys = {TYPOLOGY.NONE: "no", TYPOLOGY.SOME: "some", TYPOLOGY.ALL: "all"}
        last_updated = None

        # Iterate over the raw entries returned by the API and update data_by_section:
        for row in raw_typology_data:
            data = data_by_section[row['chapter_id']]
            key = "{video_type}_v_{problem_type}_p".format(
                video_type=friendly_keys.get(row["video_type"], "invalid"),
                problem_type=friendly_keys.get(row["problem_type"], "invalid"),
            )
            data[key] = row['num_users']
            created = self.parse_api_datetime(row['created'])
            if not last_updated or last_updated < created:
                last_updated = created

        result = []
        count_fields = [key for key in default_section_data() if key.endswith('_p')]

        # Iterate over the sections of the course in order and finalize the data for each section:
        for index, section in enumerate(self.sections_flat(), 1):
            section_id = UsageKey.from_string(section['id']).block_id
            data = data_by_section[section_id]
            data['id'] = section_id
            data['index'] = index
            data['name'] = section['display_name']
            total_active_users = sum(data[field] for field in count_fields)
            for field in count_fields:
                data[field + '_fraction'] = float(data[field]) / total_active_users if total_active_users else 0.
            result.append(data)

        return result, last_updated


class CourseEngagementVideoPresenter(CourseAPIPresenterMixin, BasePresenter):

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
        start_only_users = video['users_at_start'] - video['users_at_end']
        video.update({
            'end_percent': utils.math.calculate_percent(video['users_at_end'], total),
            'start_only_users': start_only_users,
            'start_only_percent': utils.math.calculate_percent(start_only_users, total),
        })

    def attach_aggregated_data_to_parent(self, index, parent, url_func=None):
        children = parent['children']
        total_start_users = sum(child.get('users_at_start', 0) for child in children)
        total_end_users = sum(child.get('users_at_end', 0) for child in children)
        parent.update({
            'users_at_start': total_start_users,
            'users_at_end': total_end_users,
            'index': index + 1
        })

        # calculates the percentages too
        self.attach_computed_data(parent)

        # including the URL enables navigation to child pages
        has_views = total_start_users > 0 or total_end_users > 0
        if url_func and parent['num_modules'] > 0 and has_views:
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
        if url_func:
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
        return UsageKey.from_string(module['id']).html_id()

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
