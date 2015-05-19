import urllib
import uuid

from common.tests.factories import CourseStructureFactory
from courses.tests.utils import CREATED_DATETIME_STRING


class CoursePerformanceDataFactory(CourseStructureFactory):
    """ Factory that can be used to generate data for course performance-related presenters and APIs. """

    @property
    def presented_assignments(self):
        presented = []

        # Exclude assignments with no assignment type
        assignments = [assignment for assignment in self._assignments if assignment['format']]

        for assignment_index, assignment in enumerate(assignments):
            problems = []
            for problem_index, child in enumerate(assignment['children']):
                block = self._structure['blocks'][child]

                _id = block['id']
                part_id = '{}_1_2'.format(_id)
                correct_percent = 1.0
                if problem_index == 0:
                    correct_percent = 0
                url_template = '/courses/{}/performance/graded_content/assignments/{}/problems/' \
                               '{}/parts/{}/answer_distribution/'
                problems.append({
                    'index': problem_index + 1,
                    'total_submissions': problem_index,
                    'correct_submissions': problem_index,
                    'correct_percent': correct_percent,
                    'incorrect_submissions': 0.0,
                    'incorrect_percent': 0,
                    'id': _id,
                    'name': block['display_name'],
                    'part_ids': [part_id],
                    'url': urllib.quote(url_template.format(
                        CoursePerformanceDataFactory.course_id, assignment['id'], _id, part_id))
                })

            num_problems = len(problems)
            url_template = '/courses/{}/performance/graded_content/assignments/{}/'
            presented_assignment = {
                'index': assignment_index + 1,
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'children': problems,
                'num_children': num_problems,
                'total_submissions': num_problems,
                'correct_submissions': num_problems,
                'correct_percent': 1.0,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0,
                'url': urllib.quote(url_template.format(
                    CoursePerformanceDataFactory.course_id, assignment['id']))
            }

            presented.append(presented_assignment)

        return presented

    def problems(self, graded=True):
        problems = []
        parents = self._assignments if graded else self._subsections

        for assignment in parents:
            for index, problem in enumerate(assignment['children']):
                num_submissions = index if graded else 1
                problem = self._structure['blocks'][problem]
                problems.append({
                    "module_id": problem["id"],
                    "total_submissions": num_submissions,
                    "correct_submissions": num_submissions,
                    "part_ids": ["{}_1_2".format(problem["id"])],
                    "created": CREATED_DATETIME_STRING
                })

        return problems

    @property
    def presented_grading_policy(self):
        return self._cleaned_grading_policy

    @property
    def presented_assignment_types(self):
        policies = self._cleaned_grading_policy
        return [{'name': gp['assignment_type']} for gp in policies]

    @property
    def presented_sections(self):
        presented = []
        total_submissions = 1

        for section_index, section in enumerate(self._sections):
            subsections = []
            for subsection_index, subsection in enumerate(self._subsections):
                problems = []
                for problem_index, child in enumerate(subsection['children']):
                    block = self._structure['blocks'][child]

                    _id = block['id']
                    part_id = '{}_1_2'.format(_id)
                    correct_percent = 1.0
                    url_template = '/courses/{}/performance/ungraded_content/sections/{}/subsections/' \
                                   '{}/problems/{}/parts/{}/answer_distribution/'
                    problems.append({
                        'index': problem_index + 1,
                        'total_submissions': total_submissions,
                        'correct_submissions': total_submissions,
                        'correct_percent': correct_percent,
                        'incorrect_submissions': 0.0,
                        'incorrect_percent': 0,
                        'id': _id,
                        'name': block['display_name'],
                        'part_ids': [part_id],
                        'children': [],
                        'url': urllib.quote(url_template.format(
                            CoursePerformanceDataFactory.course_id, section['id'],
                            subsection['id'], _id, part_id))
                    })

                num_problems = len(problems)
                url_template = '/courses/{}/performance/ungraded_content/sections/{}/subsections/{}/'
                presented_subsection = {
                    'index': subsection_index + 1,
                    'id': subsection['id'],
                    'name': subsection['display_name'],
                    'children': problems,
                    'num_children': num_problems,
                    'total_submissions': num_problems,
                    'correct_submissions': num_problems,
                    'correct_percent': 1.0,
                    'incorrect_submissions': 0,
                    'incorrect_percent': 0.0,
                    'url': urllib.quote(url_template.format(
                        CoursePerformanceDataFactory.course_id, section['id'],
                        subsection['id']))
                }
                subsections.append(presented_subsection)

            num_problems = 1
            url_template = '/courses/{}/performance/ungraded_content/sections/{}/'
            presented_sections = {
                'index': section_index + 1,
                'id': section['id'],
                'name': section['display_name'],
                'children': subsections,
                'num_children': num_problems,
                'total_submissions': num_problems,
                'correct_submissions': num_problems,
                'correct_percent': 1.0,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0,
                'url': urllib.quote(url_template.format(
                    CoursePerformanceDataFactory.course_id, section['id']))
            }

            presented.append(presented_sections)

        return presented


class CourseEngagementDataFactory(CourseStructureFactory):

    def _generate_subsection_children(self, assignment_type, display_name, video_index, graded):
        video = self._generate_block('video', assignment_type,
                                     '{} Video {}'.format(display_name, video_index),
                                     graded)
        self._structure['blocks'][video['id']] = video
        return video

    @property
    def presented_sections(self):
        presented = []

        for section_index, section in enumerate(self._sections):
            subsections = []
            for subsection_index, subsection in enumerate(self._subsections):
                videos = []
                for module_index, child in enumerate(subsection['children']):
                    block = self._structure['blocks'][child]

                    _id = block['id']
                    url_template = '/courses/{}/engagement/videos/sections/{}/subsections/' \
                                   '{}/modules/{}/timeline'
                    videos.append({
                        'index': module_index + 1,
                        'start_views': 10,
                        'end_views': 0,
                        'id': _id,
                        'name': block['display_name'],
                        'children': [],
                        'url': urllib.quote(url_template.format(
                            CourseEngagementDataFactory.course_id, section['id'],
                            subsection['id'], _id)),
                        'pipeline_video_id': 'edX/DemoX/Demo_Course|i4x-edX_Demo_Course-video-{}'.format(
                            uuid.uuid4().hex)
                    })

                num_videos = len(videos)
                url_template = '/courses/{}/engagement/videos/sections/{}/subsections/{}/'
                presented_subsection = {
                    'index': subsection_index + 1,
                    'id': subsection['id'],
                    'name': subsection['display_name'],
                    'children': videos,
                    'num_children': num_videos,
                    'start_views': 10,
                    'end_views': 0,
                    'url': urllib.quote(url_template.format(
                        CourseEngagementDataFactory.course_id, section['id'],
                        subsection['id']))
                }
                subsections.append(presented_subsection)

            num_problems = 1
            url_template = '/courses/{}/engagement/videos/sections/{}/'
            presented_sections = {
                'index': section_index + 1,
                'id': section['id'],
                'name': section['display_name'],
                'children': subsections,
                'num_children': num_problems,
                'start_views': 10,
                'end_views': 0,
                'url': urllib.quote(url_template.format(
                    CourseEngagementDataFactory.course_id, section['id']))
            }

            presented.append(presented_sections)

        return presented

    def get_video_timeline_api_response(self, min_segment=10, max_segment=100):
        return self._get_video_segments(min_segment, max_segment)

    def get_presented_video_timeline(self, segment_length=5, min_segment=10, max_segment=100, duration=500):
        # this video timeline has all the gaps filled in
        segments = self._get_video_segments(0, max_segment)
        for i in range(min_segment):
            segment = segments[i]
            segment.update({
                'num_users': 0,
                'num_views': 0
            })

        for segment in segments:
            segment.update({
                'start_time': segment['segment'] * segment_length,
                'num_replays': segment['num_views'] - segment['num_users']
            })

        if max_segment * segment_length <= duration:
            current_time = max_segment * segment_length

            # fill in the remainder of the video with zeros
            while current_time < (duration-segment_length):
                current_time += segment_length
                segments.append({
                    'start_time': current_time,
                    'num_replays': 0,
                    'num_users': 0,
                    'num_views': 0,
                })

            # the video may end within the bounds of a segment bucket, so fill in the last
            # point at the actual video ending
            if current_time <= duration:
                last_segment = segments[-1]
                segments.append({
                    'start_time': duration,
                    'num_replays': last_segment['num_replays'],
                    'num_users': last_segment['num_users'],
                    'num_views': last_segment['num_views'],
                })

        return segments

    def _get_video_segments(self, segment_min, segment_max):
        segments = []
        for i in range(segment_min, segment_max):
            segments.append({
                'segment': i,
                'num_users': i,
                'num_views': i * 2,
                'created': CREATED_DATETIME_STRING
            })
        return segments
