EVENT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def gene_timeline(orgnodes_list, orgpath_list, initial_zoom):
    events = []
    alldate = []

    def add_event(node, startdate, enddate=None):
        if not startdate:
            return
        i = len(events)
        ev = {
            'title': node.Heading(),
            'id': 'orgviz-timeline-{0}'.format(i),
            'startdate': startdate.strftime(EVENT_DATE_FORMAT),
            # maybe importance should be >= initial_zoom?
            "importance": initial_zoom,
            # @/static/lib/timeglider/js/timeglider/icons/
            "icon": "circle_blue.png",
            }
        alldate.append(startdate)
        if enddate:
            ev['enddate'] = enddate.strftime(EVENT_DATE_FORMAT)
            alldate.append(enddate)
        events.append(ev)

    for (orgnodes, orgpath) in zip(orgnodes_list, orgpath_list):
        for node in orgnodes:
            add_event(node, node.Scheduled())
            add_event(node, node.Deadline())
            for date in node.DateList():
                add_event(node, date)
            for (start, end) in node.RangeList():
                add_event(node, start, end)

    mindate = min(alldate)
    maxdate = max(alldate)
    center = mindate + (maxdate - mindate) / 2
    return [{
        "id": "orgviz-timeline",
        "title": "Time line",
        "initial_zoom": initial_zoom,
        # "timezone": "-07:00",
        "events": events,
        "focus_date": center.strftime(EVENT_DATE_FORMAT),
        }]
