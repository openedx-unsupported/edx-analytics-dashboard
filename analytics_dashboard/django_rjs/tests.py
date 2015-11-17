from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from django_rjs.templatetags.rjs import get_rjs_path


class RjsTests(TestCase):
    def test_get_rjs_path(self):
        rjs_dir = 'rjs-test'
        path = 'js/test.js'

        # The path should not be modified if r.js optimization is disabled.
        with self.settings(RJS_OPTIMIZATION_ENABLED=False):
            actual = get_rjs_path(path)
            self.assertEqual(actual, path)

        with self.settings(RJS_OPTIMIZATION_ENABLED=True):
            # An exception should be raised if optimization is enabled but no output directory is configured.
            with self.settings(RJS_OUTPUT_DIR=None):
                self.assertRaises(ImproperlyConfigured, get_rjs_path, path)

            # If optimization is enabled and a directory configured, the directory should be prepended to the path.
            with self.settings(RJS_OUTPUT_DIR=rjs_dir):
                actual = get_rjs_path(path)
                self.assertEqual(actual, rjs_dir + '/' + path)
