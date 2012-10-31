EVENT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def gene_timeline(orgnodes):
    events = []

    def add_event(node, startdate, enddate=None):
        if not startdate:
            return
        ev = {
            'title': node.heading,
            'start': startdate.strftime(EVENT_DATE_FORMAT),
            }
        if enddate:
            ev['end'] = enddate.strftime(EVENT_DATE_FORMAT)
        events.append(ev)

    for node in orgnodes:
        add_event(node, node.scheduled.start)
        add_event(node, node.deadline.start)
        for date in node.datelist:
            add_event(node, date.start)
        for od in node.rangelist:
            add_event(node, od.start, od.end)

    return {
        "dateTimeFormat": "iso8601",
        "events": events,
        }
