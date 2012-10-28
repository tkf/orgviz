def minutestr(m):
    """
    >>> minutestr(70)
    '01:10'
    >>> minutestr(200)
    '03:20'
    """
    return '{0:02d}:{1:02d}'.format(m // 60, m % 60)


def timedeltastr(timedelta):
    hour = timedelta.seconds // 60 // 60
    min = timedelta.seconds // 60 - (hour * 60)
    return '{0:02d}:{1:02d}'.format(timedelta.days * 24 + hour, min)
