import re
from waffle import switch_is_active


def is_feature_enabled(item):
    switch_name = item.get('switch', None)

    if switch_name:
        return switch_is_active(switch_name)

    return True


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
    def natural_sort(l, field):
        """ Natural sort from Ned Batchelder - http://nedbatchelder.com/blog/200712.html#e20071211T054956 """
        l.sort(key=lambda x: sorting._alphanum_key(x[field]))
