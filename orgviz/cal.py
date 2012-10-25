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


def events_from_node_datelist(node, eid, date_in_range):
    """
    Generate list of event from ``Orgnode.Orgnode`` which has datelist
    or rangelist.
    """
    datelist = node.datelist
    rangelist = node.rangelist
    num = len(datelist) + len(rangelist)

    start_end_pairs = []
    for dt in rangelist + datelist:
        start_end_pairs.append((dt.start, dt.end))

    eventlist = []
    for (i, (dtstart, dtend)) in enumerate(start_end_pairs):
        if date_in_range(dtstart) or date_in_range(dtend):
            summary = summary_from_node(node)
            if num > 1:
                summary += " (%d/%d)" % (i + 1, num)
            event = gene_event(summary, dtstart, dtend)
            event['id'] = eid
            eventlist.append(event)

    return eventlist


def eventdata_from_event(ev, eid):
    summary = summary_from_node(ev.node)
    num = ev.group.num
    if num > 1:
        summary += " ({0}/{1})".format(ev.ig + 1, num)
    eventdata = gene_event(summary, ev.date.start, ev.date.end)
    eventdata['id'] = eid
    return eventdata


def event_from_node_scheduled(node, eid):
    """
    Generate an event from `Orgnode.Orgnode`` which has scheduled attribute.
    """
    event = gene_event(summary_from_node(node), node.scheduled)
    event['color'] = 'green'
    event['id'] = eid
    return event


def event_from_node_deadline(node, eid):
    """
    Generate an event from `Orgnode.Orgnode`` which has deadline attribute.
    """
    event = gene_event(summary_from_node(node), node.deadline)
    event['color'] = 'red'
    event['id'] = eid
    return event


def events_from_node_closed(node, eid, date_in_range):
    """
    Generate an event from `Orgnode.Orgnode`` which has closed attribute.
    """
    closed = node.closed
    if date_in_range(closed):
        event = gene_event(summary_from_node(node), closed)
        event['color'] = 'blue'
        event['id'] = eid
        yield event


def events_from_node_clock(node, eid, date_in_range):
    """
    Generate an event from `Orgnode.Orgnode`` which has clock attribute.
    """
    summary = summary_from_node(node)
    for (cstart, cend, csum) in node.clock:
        if (date_in_range(cstart) or date_in_range(cend)) and csum > 0:
            event = gene_event(summary, cstart, cend)
            event['color'] = 'blue'
            event['id'] = eid
            yield event


def events_from_node_misc(node, eid, date_in_range):
    for event in events_from_node_datelist(node, eid, date_in_range):
        event['color'] = 'gray'
        yield event


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


def get_date_in_range(start, end):
    start = datetime.datetime.fromtimestamp(start) if start else None
    end = datetime.datetime.fromtimestamp(end) if end else None

    def date_in_range(date):
        date = todate(date)
        if not isinstance(date, (datetime.datetime, datetime.date)):
            return False
        if isinstance(date, datetime.date):  # convert to datetime
            date = datetime.datetime(*date.timetuple()[:3])
        if start is not None and date < start:
            return False
        if end is not None and end < date:
            return False
        return True
    return date_in_range


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
    # FIXME: remove date_in_range later:
    date_in_range = get_date_in_range(start, end)
    events = []
    for event in nodes_to_events(
            orgnodes, eventclass=eventclass,
            filters=filters, classifier=classifier):
        if not daterange.has_overlap(event.date):
            continue
        if event.eventclass == 'scheduled':
            events.append(event_from_node_scheduled(event.node, get_new_eid()))
        elif event.eventclass == 'deadline':
            events.append(event_from_node_deadline(event.node, get_new_eid()))
        elif event.eventclass == 'closed':
            map(events.append,
                events_from_node_closed(
                    event.node, get_new_eid(), date_in_range))
        elif event.eventclass == 'clock':
            map(events.append,
                events_from_node_clock(
                    event.node, get_new_eid(), date_in_range))
        else:
            eventdata = eventdata_from_event(event)
            events.append(eventdata)
            if event.eventclass == 'none':
                eventdata['color'] = 'gray'
    return events
