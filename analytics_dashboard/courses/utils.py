import re
from waffle import switch_is_active

from opaque_keys.edx.keys import UsageKey


def is_feature_enabled(item):
    switch_name = item.get('switch', None)

    if switch_name:
        return switch_is_active(switch_name)

    return True


def get_encoded_module_id(module_id):
    """Return an encoded module ID representing `module_id`"""
    return UsageKey.from_string(module_id).html_id()


class number(object):
    @staticmethod
    def is_number(word):
        try:
            float(word)
            return True
        except ValueError:
            return False


class math(object):
    @staticmethod
    def calculate_percent(count, total):
        return count / float(total) if total > 0 else 0.0


class sorting(object):
    @staticmethod
    def _tryint(s):
        try:
            return int(s)
        except ValueError:
            return s

    @staticmethod
    def _alphanum_key(s):
        """
        Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
        """
        return [sorting._tryint(c) for c in re.split('([0-9]+)', s)]

    @staticmethod
    def natural_sort(l, field=None):
        """ Natural sort from Ned Batchelder - http://nedbatchelder.com/blog/200712.html#e20071211T054956 """
        if field:
            l.sort(key=lambda x: sorting._alphanum_key(x[field]))
        else:
            l.sort(key=sorting._alphanum_key)
