from orgparse.date import total_seconds, total_minutes


def minutestr(m):
    """
    Convert an integer to a 'HH:MM'-format string.

    >>> minutestr(70)
    '01:10'
    >>> minutestr(200)
    '03:20'
    >>> minutestr(180 * 60 + 30)
    '180:30'

    """
    return '{0:02d}:{1:02d}'.format(m // 60, m % 60)


def timedeltastr(timedelta):
    """
    Convert a `datetime.timedelta` object to a 'HH:MM'-format string.

    >>> import datetime
    >>> timedeltastr(datetime.timedelta(1, 2 * 60 * 60 + 30 * 60))
    '26:30'

    """
    return minutestr(int(total_minutes(timedelta)))
