import time

def get_formatted_date(time_interval):
    """
    Make the date human readable
    """
    struct_time = time.strptime(time_interval, "%Y-%m-%dT%H:%M:%SZ")
    return time.strftime('%B %d, %Y', struct_time)
