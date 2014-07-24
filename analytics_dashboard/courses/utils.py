import time


def get_formatted_date_time(time_interval):
    """
    Make the date human readable
    """
    struct_time = time.strptime(time_interval, "%Y-%m-%dT%H:%M:%SZ")
    return time.strftime('%B %d, %Y', struct_time)


def get_formatted_date(date):
    """
    Make the date human readable.

    Arguments:
        date (Date): Date to be formatted.
    """
    struct_time = time.strptime(date, "%Y-%m-%d")
    return time.strftime('%B %d, %Y', struct_time)


def get_formatted_summary_number(maybe_number):
    """
    Return n/a or a formatted number with commas.

    Arguments:
        maybe_number: None or an int.
    """
    if maybe_number is None:
        label = 'n/a'
    else:
        label = "{:,}".format(maybe_number)

    return label
