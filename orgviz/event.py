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

    def __getattr__(self, name):
        return getattr(self.node, name)


def single_node_to_events(node, **kwds):
    if node.scheduled:
        yield Event(node.scheduled, node)
    if node.deadline:
        yield Event(node.deadline, node)
    if node.closed:
        yield Event(node.closed, node)
    if node.clock:
        yield Event(node.clock, node)
    for date in node.datelist:
        yield Event(date, node, **kwds)
    for date in node.rangelist:
        yield Event(date, node, **kwds)


def _nodes_to_events(nodes, **kwds):
    for nd in nodes:
        for ev in single_node_to_events(nd, **kwds):
            yield ev


def nodes_to_events(nodes, filters=[], eventclass=[], classifier=None):
    """
    Iterate over events in org nodes.

    :arg iterable nodes:
        Iterable of org node.

    :type  filters: list of callable
    :arg   filters:
        Each function is called with event object.  Event is included
        only when all the functions return True.

    :type  eventclass: str or list of str
    :arg   eventclass:
        Event class to include.

    :type  classifier: None or callable
    :arg   classifier:
        A function to determine eventclass of a event, when it cannot
        be determined by other method.

    """
    if isinstance(eventclass, basestring):
        eventclass = [eventclass]
    for ev in _nodes_to_events(classifier=classifier):
        if not all(f(ev) for f in filters):
            continue
        if ev.eventclass in eventclass:
            yield ev
