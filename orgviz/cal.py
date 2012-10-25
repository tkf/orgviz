import time
import datetime

import orgparse.date

from .event import nodes_to_events


def summary_from_node(node):
    heading = node.heading
    tags = node.tags
    if tags:
        summary = "%s [%s]" % (heading, "|".join(tags))
        return summary
    else:
        return heading


def dt2ut(dt):
    """Convert datetime/date to unix time"""
    # see: http://www.seehuhn.de/pages/pdate#unix
    return time.mktime(dt.timetuple())


def todate(date):
    """
    Convert OrgDate object to datetime, return as-is for other types.
    """
    if isinstance(date, orgparse.date.OrgDate):
        return date.start
    else:
        return date


def gene_event(summary, dtstart, dtend=None):
    dtstart = todate(dtstart)
    dtend = todate(dtend)
    event = {
        'title': summary,
        'start': dt2ut(dtstart),
        }
    if isinstance(dtstart, datetime.datetime):
        event['allDay'] = False
    elif isinstance(dtstart, datetime.date):
        event['allDay'] = True
    if dtend is not None:
        event['end'] = dt2ut(dtend)
    return event


def match_tag(candidate, taglist, default):
    """
    Return a first matched tag in both ``candidate`` and ``taglist``
    if exists, else ``default``.

    Examples
    --------
    >>> match_tag([1,2,3], [2,3,4], 0)
    2
    >>> match_tag([1,2,3], [3,2,4], 0)
    3
    >>> match_tag([1,2,3], [4,5,6], 0)
    0

    """
    for t in taglist:
        if t in candidate:
            return t
    return default  # if any tag in `candidate` is not in `taglist`


EVENTCLASS_COLOR_MAP = {
    'scheduled': 'green',
    'deadline': 'red',
    'closed': 'blue',
    'clock': 'blue',
    'none': 'gray',
}


def eventdata_from_event(ev, eid):
    summary = summary_from_node(ev.node)
    num = ev.group.num
    if num > 1:
        summary += " ({0}/{1})".format(ev.ig + 1, num)
    eventdata = gene_event(summary, ev.date.start, ev.date.end)
    color = EVENTCLASS_COLOR_MAP.get(ev.eventclass)
    if color:
        eventdata['color'] = color
    eventdata['id'] = eid
    return eventdata


def gene_get_new_eid():
    """
    Generate unique id getter function

    Examples
    --------
    >>> getter = gene_get_new_eid()
    >>> getter()
    0
    >>> getter()
    1
    >>> [getter() for _ in range(10)]
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    """
    def get_new_eid():
        i = 0
        while True:
            yield i
            i += 1
    getter = get_new_eid()
    return getter.next


def gene_events(orgnodes, eventclass, filters, classifier, start, end):
    """
    Return a list of event data for FullCalendar.

    :type   orgnodes: iterative
    :arg    orgnodes: yields orgparse.node.OrgNode objects
    :type eventclass: list of str
    :arg  eventclass: e.g., ``['deadline', 'scheduled']``
    :type    filters: list of functions
    :arg     filters: functions specified in `ORG_CAL_FILTERS`.
    :type classifier: function
    :arg  classifier: function specified by `ORG_CAL_EVENT_CLASSIFIER`
    :type      start: int or None
    :arg       start: timestamp
    :type        end: int or None
    :arg         end: timestamp

    """
    get_new_eid = gene_get_new_eid()
    daterange = orgparse.date.OrgDate(start, end)
    events = []
    for event in nodes_to_events(
            orgnodes, eventclass=eventclass,
            filters=filters, classifier=classifier):
        if not daterange.has_overlap(event.date):
            continue
        if isinstance(event.date, orgparse.date.OrgDateClock) and \
               event.date.duration <= 0:
            continue
        eventdata = eventdata_from_event(event, get_new_eid())
        events.append(eventdata)
    return events
