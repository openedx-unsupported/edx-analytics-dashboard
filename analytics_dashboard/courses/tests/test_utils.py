import datetime
from django.test import TestCase

import courses.utils as utils


class UtilsTest(TestCase):
    def test_get_formatted_date_time(self):
        actualDate = utils.get_formatted_date_time('2013-01-01T12:12:12Z')
        self.assertEqual(actualDate, 'January 01, 2013')

    def test_get_formatted_date(self):
        actualDate = utils.get_formatted_date('2013-01-01')
        self.assertEqual(actualDate, 'January 01, 2013')

    def test_get_formatted_summary_number(self):
        actual = utils.get_formatted_summary_number(None)
        self.assertEqual(actual, 'n/a')

        actual = utils.get_formatted_summary_number(1000)
        self.assertEqual(actual, '1,000')

        actual = utils.get_formatted_summary_number(-9433312)
        self.assertEqual(actual, '-9,433,312')
