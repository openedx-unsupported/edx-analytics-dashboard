from django.test import TestCase

from courses.utils import get_formatted_date

class UtilsTest(TestCase):

    def test_get_formatted_date(self):
        actualDate = get_formatted_date('2013-01-01T12:12:12Z')
        self.assertEqual(actualDate, 'January 01, 2013')
