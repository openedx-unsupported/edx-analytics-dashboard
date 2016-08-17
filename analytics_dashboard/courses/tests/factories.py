import hashlib
import re
import uuid

from collections import OrderedDict
from slugify import slugify

from common.tests.factories import CourseStructureFactory
from courses.tests.utils import CREATED_DATETIME_STRING
from courses import utils


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
                    correct_percent = 0.0
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
                    'url': url_template.format(
                        self.course_id, assignment['id'], _id, part_id)
                })

            num_problems = len(problems)
            num_problems_float = float(num_problems)
            url_template = '/courses/{}/performance/graded_content/assignments/{}/'
            presented_assignment = {
                'index': assignment_index + 1,
                'id': assignment['id'],
                'name': assignment['display_name'],
                'assignment_type': assignment['format'],
                'children': problems,
                'num_modules': num_problems,
                'total_submissions': num_problems,
                'correct_submissions': num_problems,
                'correct_percent': 1.0,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0,
                'average_submissions': num_problems / num_problems_float,
                'average_correct_submissions': num_problems / num_problems_float,
                'average_incorrect_submissions': 0.0,
                'url': url_template.format(
                    self.course_id, assignment['id'])
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
        url_template = '/courses/{}/performance/graded_content/{}/'
        return [
            {
                'name': gp['assignment_type'],
                'url': url_template.format(self.course_id, slugify(gp['assignment_type']))

            } for gp in policies
        ]

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
                        'url': url_template.format(
                            self.course_id, section['id'],
                            subsection['id'], _id, part_id)
                    })

                num_problems = len(problems)
                num_problems_float = float(num_problems)
                url_template = '/courses/{}/performance/ungraded_content/sections/{}/subsections/{}/'
                presented_subsection = {
                    'index': subsection_index + 1,
                    'id': subsection['id'],
                    'name': subsection['display_name'],
                    'children': problems,
                    'num_modules': num_problems,
                    'total_submissions': num_problems,
                    'correct_submissions': num_problems,
                    'correct_percent': 1.0,
                    'incorrect_submissions': 0,
                    'incorrect_percent': 0.0,
                    'average_submissions': num_problems / num_problems_float,
                    'average_correct_submissions': num_problems / num_problems_float,
                    'average_incorrect_submissions': 0.0,
                    'url': url_template.format(
                        self.course_id, section['id'],
                        subsection['id'])
                }
                subsections.append(presented_subsection)

            num_problems = 1
            num_problems_float = float(num_problems)
            url_template = '/courses/{}/performance/ungraded_content/sections/{}/'
            presented_sections = {
                'index': section_index + 1,
                'id': section['id'],
                'name': section['display_name'],
                'children': subsections,
                'num_modules': num_problems,
                'total_submissions': num_problems,
                'correct_submissions': num_problems,
                'correct_percent': 1.0,
                'incorrect_submissions': 0,
                'incorrect_percent': 0.0,
                'average_submissions': num_problems / num_problems_float,
                'average_correct_submissions': num_problems / num_problems_float,
                'average_incorrect_submissions': 0.0,
                'url': url_template.format(
                    self.course_id, section['id'])
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
                        'users_at_start': 10,
                        'users_at_end': 0,
                        'id': _id,
                        'name': block['display_name'],
                        'children': [],
                        'url': url_template.format(
                            self.course_id, section['id'],
                            subsection['id'], _id),
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
                    'num_modules': num_videos,
                    'users_at_start': 10,
                    'users_at_end': 0,
                    'url': url_template.format(
                        self.course_id, section['id'],
                        subsection['id'])
                }
                subsections.append(presented_subsection)

            url_template = '/courses/{}/engagement/videos/sections/{}/'
            presented_sections = {
                'index': section_index + 1,
                'id': section['id'],
                'name': section['display_name'],
                'children': subsections,
                'num_modules': 1,
                'users_at_start': 10,
                'users_at_end': 0,
                'url': url_template.format(
                    self.course_id, section['id'])
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

    def videos(self):
        """
        Mock video data.
        """
        videos = [
            {
                "pipeline_video_id": "edX/DemoX/Demo_Course|i4x-edX-DemoX-video-7e9b434e6de3435ab99bd3fb25bde807",
                "encoded_module_id": "i4x-edX-DemoX-video-7e9b434e6de3435ab99bd3fb25bde807",
                "duration": 257,
                "segment_length": 5,
                "users_at_start": 10,
                "users_at_end": 0,
                "created": "2015-04-15T214158"
            },
            {
                "pipeline_video_id": "edX/DemoX/Demo_Course|i4x-edX-DemoX-videoalpha-0b9e39477cf34507a7a48f74be381fdd",
                "encoded_module_id": "i4x-edX-DemoX-videoalpha-0b9e39477cf34507a7a48f74be381fdd",
                "duration": 195,
                "segment_length": 5,
                "users_at_start": 55,
                "users_at_end": 0,
                "created": "2015-04-15T214158"
            }
        ]
        return videos


class TagsDistributionDataFactory(CourseStructureFactory):

    _count_of_homework_assignments = 0
    _tags_structure = None

    def __init__(self, tags_data_per_homework_assigment):
        self._count_of_problems = len(tags_data_per_homework_assigment) + 1
        self.tags_data_per_homework_assigment = tags_data_per_homework_assigment

        super(TagsDistributionDataFactory, self).__init__()
        for policy in self.grading_policy:
            if policy['assignment_type'].startswith('Homework'):
                self._count_of_homework_assignments = policy['count']
                break
        self._generate_tags_structure()

    def _get_block_id(self, block_type, block_format=None, display_name=None, graded=True, children=None):
        if display_name:
            return hashlib.md5(display_name).hexdigest()
        else:
            return super(TagsDistributionDataFactory, self)._get_block_id(block_type, block_format, display_name,
                                                                          graded, children)

    def _generate_tags_structure(self):
        reg = re.compile(r'Homework (\d) Problem (\d)')
        tags_data = {}

        for k, item in self._structure['blocks'].iteritems():
            if item['type'] == 'problem' and item['display_name'].startswith('Homework'):
                m = reg.match(item['display_name'])
                assig_num = int(m.group(1))
                problem_num = int(m.group(2)) - 1
                key = assig_num * 10 + problem_num
                tags_data[key] = {
                    "display_name": item['display_name'],
                    "module_id": item['id'],
                    "total_submissions": self.tags_data_per_homework_assigment[problem_num]['total_submissions'],
                    "correct_submissions": self.tags_data_per_homework_assigment[problem_num]['correct_submissions'],
                    "tags": self.tags_data_per_homework_assigment[problem_num]['tags'],
                }
        self._tags_structure = [tags_data[k] for k in sorted(tags_data)]

    @property
    def problems_and_tags(self):
        """
        Mock tags distribution data.
        """
        return self._tags_structure

    def get_expected_available_tags(self):
        tags = {}
        for item in self.tags_data_per_homework_assigment:
            for key, val in item['tags'].iteritems():
                if key not in tags:
                    tags[key] = set()
                tags[key].add(val)
        return tags

    def get_expected_learning_outcome_tags_content_nav(self, key):
        url_template = '/courses/{}/performance/learning_outcomes/{}/'
        expected_available_tags = self.get_expected_available_tags()
        if key in expected_available_tags:
            return [{'id': v, 'name': v, 'url': url_template.format(self.course_id, slugify(v))}
                    for v in expected_available_tags[key]]
        else:
            return []

    def get_expected_tags_distribution(self, tag_key):
        index = 0
        expected = OrderedDict()
        k = self._count_of_homework_assignments

        for val in self.tags_data_per_homework_assigment:
            if tag_key in val['tags']:
                tag_value = val['tags'][tag_key]
                if tag_value not in expected:
                    index += 1
                    expected[tag_value] = {
                        "id": tag_value,
                        "index": index,
                        "name": tag_value,
                        "total_submissions": 0,
                        "correct_submissions": 0,
                        "incorrect_submissions": 0,
                        "num_modules": 0
                    }

                incorrect_submissions = val["total_submissions"] - val["correct_submissions"]

                expected[tag_value]["total_submissions"] += val["total_submissions"] * k
                expected[tag_value]["correct_submissions"] += val["correct_submissions"] * k
                expected[tag_value]["incorrect_submissions"] += incorrect_submissions * k
                expected[tag_value]["num_modules"] += k

        url_template = '/courses/{}/performance/learning_outcomes/{}/'

        for tag_val, item in expected.iteritems():
            item.update({
                'average_submissions': (item['total_submissions'] * 1.0) / item['num_modules'],
                'average_correct_submissions': (item['correct_submissions'] * 1.0) / item['num_modules'],
                'average_incorrect_submissions': (item['incorrect_submissions'] * 1.0) / item['num_modules'],
                'correct_percent': utils.math.calculate_percent(item['correct_submissions'],
                                                                item['total_submissions']),
                'incorrect_percent': utils.math.calculate_percent(item['incorrect_submissions'],
                                                                  item['total_submissions']),
                'url': url_template.format(self.course_id, slugify(tag_val))
            })

        return expected.values()

    def get_expected_modules_marked_with_tag(self, tag_key, tag_value):
        index = 0
        expected = []
        available_tags = self.get_expected_available_tags()

        url_template = '/courses/{}/performance/learning_outcomes/{}/problems/{}/'

        for i in xrange(1, self._count_of_homework_assignments + 1):
            num = 0
            for val in self.tags_data_per_homework_assigment:
                num += 1
                if tag_key in val['tags'] and val['tags'][tag_key] == tag_value:
                    display_name = 'Homework %d Problem %d' % (i, num)
                    incorrect_submissions = val["total_submissions"] - val["correct_submissions"]
                    new_item_id = 'i4x://edX/DemoX/problem/%s' % hashlib.md5(display_name).hexdigest()
                    index += 1
                    new_item = {
                        'id': new_item_id,
                        'index': index,
                        'name': ', '.join(['Demo Course', 'Homework %d' % i, display_name]),
                        'total_submissions': val['total_submissions'],
                        'correct_submissions': val['correct_submissions'],
                        'incorrect_submissions': incorrect_submissions,
                        'correct_percent': utils.math.calculate_percent(val['correct_submissions'],
                                                                        val['total_submissions']),
                        'incorrect_percent': utils.math.calculate_percent(incorrect_submissions,
                                                                          val['total_submissions']),
                        'url': url_template.format(self.course_id, slugify(tag_value), new_item_id)
                    }
                    if available_tags:
                        for av_tag_key in available_tags:
                            if av_tag_key in val['tags']:
                                new_item[av_tag_key] = val['tags'][av_tag_key]
                            else:
                                new_item[av_tag_key] = None
                    expected.append(new_item)
        return expected
