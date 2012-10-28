import time
import datetime

from .event import nodes_to_events


def summary_from_node(node):
    heading = node.heading
    tags = node.tags
    if tags:
        summary = "%s [%s]" % (heading, "|".join(tags))
        return summary
    else:
        return heading


def totimestamp(dt):
    """Convert datetime/date to unix time"""
    # see: http://www.seehuhn.de/pages/pdate#unix
    return time.mktime(dt.timetuple())


def gene_event(summary, dtstart, dtend=None):
    event = {
        'title': summary,
        'start': totimestamp(dtstart),
        }
    if isinstance(dtstart, datetime.datetime):
        event['allDay'] = False
    elif isinstance(dtstart, datetime.date):
        event['allDay'] = True
    if dtend is not None:
        event['end'] = totimestamp(dtend)
    return event


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
    events = []
    for (eid, event) in enumerate(nodes_to_events(
            orgnodes, eventclass=eventclass,
            filters=filters, classifier=classifier,
            start=start, end=end)):
        if not getattr(event.date, 'duration', True):
            continue
        eventdata = eventdata_from_event(event, eid)
        events.append(eventdata)
    return events
