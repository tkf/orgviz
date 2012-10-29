EVENT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def gene_timeline(orgnodes_list, orgpath_list, initial_zoom):
    events = []
    alldate = []

    def add_event(node, startdate, enddate=None):
        if not startdate:
            return
        ev = {
            'title': node.heading,
            'start': startdate.strftime(EVENT_DATE_FORMAT),
            }
        alldate.append(startdate)
        if enddate:
            ev['end'] = enddate.strftime(EVENT_DATE_FORMAT)
            alldate.append(enddate)
        events.append(ev)

    for (orgnodes, orgpath) in zip(orgnodes_list, orgpath_list):
        for node in orgnodes:
            add_event(node, node.scheduled)
            add_event(node, node.deadline)
            for date in node.datelist:
                add_event(node, date)
            for od in node.rangelist:
                add_event(node, od.start, od.end)

    return {
        "dateTimeFormat": "iso8601",
        "events": events,
        }
