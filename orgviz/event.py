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

    def __init__(self, date, node, eventclass=None):
        self._date = date
        self._node = node
        self._eventclass = eventclass

    @property
    def eventclass(self):
        if self._eventclass:
            return self._eventclass
        else:
            for (ec, dc) in EVENTCLASS_DATECLASS_MAP:
                if isinstance(self.date, dc):
                    return ec

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


def single_node_to_events(node):
    if node.scheduled:
        yield Event(node.scheduled, node)
    if node.deadline:
        yield Event(node.deadline, node)
    if node.closed:
        yield Event(node.closed, node)
    if node.clock:
        yield Event(node.clock, node)
    for date in node.datelist:
        yield Event(date, node)
    for date in node.rangelist:
        yield Event(date, node)


def nodes_to_events(nodes):
    for nd in nodes:
        for ev in single_node_to_events(nd):
            yield ev
