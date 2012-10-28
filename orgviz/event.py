from orgparse import date

EVENTCLASS_DATECLASS_MAP = [
    ('scheduled', date.OrgDateScheduled),
    ('deadline', date.OrgDateDeadline),
    ('closed', date.OrgDateClosed),
    ('clock', date.OrgDateClock),
]


class Event(object):

    """
    A class representing event.

    Let's quickly create an org node and make an event from it:

    >>> from orgparse import loads
    >>> node = loads('''
    ... * Node                  :TAG:
    ...   SCHEDULED: <2012-02-26 Sun>
    ... ''').children[0]
    >>> ev = Event(node.scheduled, node)

    Simple usage:

    >>> ev.eventclass
    'scheduled'
    >>> ev.date
    OrgDateScheduled((2012, 2, 26))
    >>> ev.node                                        # doctest: +ELLIPSIS
    <orgparse.node.OrgNode object at 0x...>
    >>> ev.filename  # this will be a real path if you load from a file
    '<string>'

    You can directly access to org node attributes:

    >>> 'TAG' in ev.tags
    True
    >>> ev.heading
    'Node'

    """

    def __init__(self, date, node, eventclass=None, classifier=None):
        self._date = date
        self._node = node
        self._eventclass = eventclass
        self._classifier = classifier

    @property
    def eventclass(self):
        if self._eventclass:
            return self._eventclass
        else:
            for (ec, dc) in EVENTCLASS_DATECLASS_MAP:
                if isinstance(self.date, dc):
                    return ec
        if self._classifier:
            return self._classifier(self.node) or 'none'
        return 'none'

    @property
    def date(self):
        """
        Org date object.
        """
        return self._date

    @property
    def node(self):
        """
        Org node object.
        """
        return self._node

    @property
    def filename(self):
        """
        Path to org-mode file.
        """
        return self.node.env.filename

    @property
    def group(self):
        """
        :class:`EventGroup` object.
        """
        return self._group

    @property
    def ig(self):
        """
        Return the index in event group.
        """
        return self._ig

    def __getattr__(self, name):
        return getattr(self.node, name)


class EventGroup(object):

    """
    A class to make group of :class:`Event` objects with same eventclass.
    """

    def __init__(self):
        self._events = []

    @property
    def num(self):
        """
        Number of event in this group
        """
        return len(self._events)

    def _append(self, ev):
        ev._group = self
        ev._ig = self.num
        self._events.append(ev)


def grouper(events_generator):
    def wrapper(*args, **kwds):
        groups = {}
        for event in events_generator(*args, **kwds):
            ec = event.eventclass
            if ec in groups:
                evgroup = groups[ec]
            else:
                evgroup = EventGroup()
                groups[ec] = evgroup
            evgroup._append(event)
            yield event
    return wrapper


@grouper
def single_node_to_events(node, **kwds):
    if node.scheduled:
        yield Event(node.scheduled, node)
    if node.deadline:
        yield Event(node.deadline, node)
    if node.closed:
        yield Event(node.closed, node)
    for clock in node.clock:
        yield Event(clock, node)
    for date in node.datelist:
        yield Event(date, node, **kwds)
    for date in node.rangelist:
        yield Event(date, node, **kwds)


def _nodes_to_events(nodes, **kwds):
    for nd in nodes:
        for ev in single_node_to_events(nd, **kwds):
            yield ev


def nodes_to_events(nodes, filters=[], eventclass='all', classifier=None,
                    start=None, end=None):
    """
    Iterate over events in org nodes.

    :arg iterable nodes:
        Iterable of org node.

    :type  filters: list of callable
    :arg   filters:
        Each function is called with an event object.  Event is
        included only when all the functions return True.
        `ORG_CAL_FILTERS` is used for this argument.

    :type  eventclass: str or list of str
    :arg   eventclass:
        Event class to include.
        JS client specifies this argument via `event_dates` request.

    :type  classifier: None or callable
    :arg   classifier:
        A function to determine eventclass of a event, when it cannot
        be determined by other method.
        `ORG_CAL_EVENT_CLASSIFIER` is used for this argument.

    :type  start: anything `date.OrgDateClock` can handle
    :arg   start: timestamp
    :type    end: anything `date.OrgDateClock` can handle
    :arg     end: timestamp

    >>> from orgparse import loads
    >>> nodes = loads('''
    ... * Node 1
    ...   SCHEDULED: <2012-02-26 Sun>
    ... * Node 2
    ...   <2012-02-24 Fri>, <2012-02-25 Sat>
    ... ''').env.nodes[1:]
    >>> events = list(nodes_to_events(nodes))
    >>> events                   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [<orgviz.event.Event object at 0x...>,
     <orgviz.event.Event object at 0x...>,
     <orgviz.event.Event object at 0x...>]
    >>> events[0].eventclass
    'scheduled'
    >>> events[1].eventclass
    'none'
    >>> events[2].eventclass
    'none'
    >>> events[0].group.num
    1
    >>> events[1].group.num
    2
    >>> events[0].group is not events[1].group
    True
    >>> events[1].group is not events[2].group
    False
    >>> events[0].ig
    0
    >>> events[1].ig
    0
    >>> events[2].ig
    1

    >>> only_date_list = lambda ev: ev.node.datelist
    >>> events = list(nodes_to_events(nodes, filters=[only_date_list]))
    >>> events                   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [<orgviz.event.Event object at 0x...>]
    >>> events[0].node.heading
    'Node 2'

    >>> events = list(nodes_to_events(nodes, eventclass=['scheduled']))
    >>> events                   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [<orgviz.event.Event object at 0x...>]
    >>> events[0].node.heading
    'Node 1'

    >>> events = list(nodes_to_events(nodes, classifier=lambda _: 'spam'))
    >>> events                   # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [<orgviz.event.Event object at 0x...>,
     <orgviz.event.Event object at 0x...>,
     <orgviz.event.Event object at 0x...>]
    >>> events[1].eventclass
    'spam'

    """
    if start is None or end is None:
        date_in_range = lambda _: True
    else:
        date_in_range = date.OrgDate(start, end).has_overlap
    if isinstance(eventclass, basestring) and eventclass != 'all':
        raise ValueError("`eventclass` must be a list or string 'all'.")
    for ev in _nodes_to_events(nodes, classifier=classifier):
        if not date_in_range(ev.date):
            continue
        if eventclass != 'all' and ev.eventclass not in eventclass:
            continue
        if not all(f(ev) for f in filters):
            continue
        yield ev
