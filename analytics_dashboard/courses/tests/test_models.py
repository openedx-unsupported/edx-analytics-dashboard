import mock

from django.test import TestCase

import analyticsclient.activity_type as AT

from courses.models import StudentEngagement

class StudentEngagementTest(TestCase):

    def mock_activity_data(activity_type):
        activity_types = [AT.ANY, AT.ATTEMPTED_PROBLEM, AT.PLAYED_VIDEO,
                          AT.POSTED_FORUM]

        summaries = {}
        count = 0
        for activity in activity_types:
            summaries[activity] = {
                'interval_end': 'this is a time ' + str(count),
                'activity_type': activity,
                'count': 100 * count
            }
            count = count + 1

        return summaries[activity_type]

    @mock.patch('analyticsclient.course.Course.recent_activity', mock.Mock(side_effect=mock_activity_data, autospec=True))
    def test_get_summary(self):
        student_engagement = StudentEngagement()
        summary = student_engagement.get_summary('this/course/id')
        # make sure that we get the time from "ANY"
        self.assertEqual(summary['interval_end'], 'this is a time 0')

        # make sure that activity counts all match up
        self.assertEqual(summary[AT.ANY], 0)
        self.assertEqual(summary[AT.ATTEMPTED_PROBLEM], 100)
        self.assertEqual(summary[AT.PLAYED_VIDEO], 200)
        self.assertEqual(summary[AT.POSTED_FORUM], 300)
