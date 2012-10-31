"""
Generate graphs from org files to visualize how you manage tasks
"""

import matplotlib
matplotlib.use('Agg')
import pylab
import numpy
from matplotlib.dates import date2num
import datetime

from .event import nodes_to_events
from .utils.date import total_seconds

## timezone = matplotlib.dates.pytz.timezone('Europe/Paris')
## xa_formatter = matplotlib.dates.DateFormatter("%b %d %H:%M", timezone)
## #xa_locator = matplotlib.dates.HourLocator(tz=timezone)
## xa_locator = matplotlib.dates.AutoDateLocator(timezone)
## xa_formatter = matplotlib.dates.AutoDateFormatter(xa_locator, timezone)

from matplotlib.dates import  DateFormatter, WeekdayLocator, \
     DayLocator, MONDAY  # , HourLocator

FIGSIZE = (4, 3)

mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()                  # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # Eg, Jan 12
dayFormatter = DateFormatter('%d')      # Eg, 12
# See:
# http://matplotlib.sourceforge.net/examples/pylab_examples/finance_demo.html


def set_xaxis_format_date(ax):
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    ## ax.xaxis.set_major_formatter(xa_formatter)
    ## ax.xaxis.set_major_locator(xa_locator)
    pylab.setp(ax.get_xticklabels(), rotation=40, ha="right")


def within_ndays_before(n):
    now = datetime.datetime.now()
    maxsec = n * 24 * 60 * 60

    def predicate(ev):
        date = ev.date.start
        if isinstance(date, datetime.date):
            date = datetime.datetime(*date.timetuple()[:3])
        return 0 <= total_seconds(now - date) <= maxsec
    return predicate


def plot_clocked_per_day(ax, orgnodes, days,
                         ylabel='Clocked Time Per Day [h]'):
    events = nodes_to_events(
        orgnodes, filters=[within_ndays_before(days)], eventclass=['clock'])
    clocked = numpy.array(
        [(date2num(e.date.start), total_seconds(e.date.duration) / 60 / 60)
         for e in events],
        dtype=[('start', int), ('duration', int)])
    if len(clocked) == 0:
        return
    lastday = clocked['start'].max()
    firstday = clocked['start'].min()

    dates = numpy.arange(lastday - firstday + 1)
    cpd = numpy.zeros(len(dates), dtype='float')  # clocked per day
    for i in dates:
        cpd[i] = numpy.extract(clocked['start'] == firstday + i,
                               clocked['duration']).sum()
    ax.bar(dates + firstday, cpd, width=1, color='b', alpha=0.3)
    ax.set_ylabel(ylabel)


def gene_clocked_par_day(orgnodes, done, days=30):
    """
    Draw graph from org files: clocked task par day
    """
    fig = pylab.figure(figsize=FIGSIZE)
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    plot_clocked_per_day(ax, orgnodes, days)
    set_xaxis_format_date(ax)
    return fig


def time_array_closed(orgnodes, done, start):
    time_array = numpy.array(date2num([c.start for c in (
        node.closed
        for node in orgnodes
        if node.todo == done
        ) if c]))
    return numpy.take(time_array, numpy.where(time_array > start))[0]


def plot_done_par_day(ax, orgnodes, done, days,
                      ylabel='Tasks done per day [1/day]'):
    today = int(date2num(datetime.datetime.now())) + 1  # end of today
    start = today - days
    time_array = time_array_closed(orgnodes, done, start)
    ax.hist(time_array, bins=days, range=(start, today),
            color='b', alpha=0.3)
    ax.set_ylabel(ylabel)


def gene_done_par_day(orgnodes, done, days=30):
    """
    Draw graph from org file: done (closed) task par day
    """
    fig = pylab.figure(figsize=FIGSIZE)
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    plot_done_par_day(ax, orgnodes, done, days)
    set_xaxis_format_date(ax)
    return fig


def plot_tags_dist(ax, orgnodes, days=180, num=10):
    event_tags = (e.tags for e in nodes_to_events(
        orgnodes,
        filters=[within_ndays_before(days)],
        eventclass=['closed']))

    counter = {}
    for tags in event_tags:
        for t in tags:
            if t in counter:
                counter[t] += 1
            else:
                counter[t] = 1

    if not counter:
        return
    taglen = max(map(len, counter))
    data = numpy.array(
        list(counter.items()),
        dtype=[('tags', 'S{0}'.format(taglen)), ('count', int)])
    data.sort(order=['count'])
    data = data[::-1][:num]
    x = numpy.arange(len(data))
    ax.bar(x, data['count'], width=1, color='b', alpha=0.3)
    ax.set_xticks(x + 0.5)
    ax.set_xticklabels(data['tags'])
    pylab.setp(ax.get_xticklabels(),
               rotation=90,
               y=0.05,
               horizontalalignment="left",
               verticalalignment='bottom')


def gene_tags_dist(orgnodes, done='THIS IS DUMMY ARG', **kwds):
    """
    Plot top N tags of closed tasks and the number of the tasks.
    """
    fig = pylab.figure(figsize=FIGSIZE)
    ax = fig.add_subplot(111)
    plot_tags_dist(ax, orgnodes, **kwds)
    return fig


def decompose_in_day_and_hour(dates):
    decomposed = numpy.zeros(len(dates), dtype=[('day', int), ('hour', float)])
    decomposed['day'] = dates
    decomposed['hour'] = (dates - decomposed['day']) * 24
    return decomposed


def plot_clocked_and_closed(ax, orgnodes, days=30):
    events = list(nodes_to_events(
        orgnodes,
        filters=[within_ndays_before(days)],
        eventclass=['closed', 'clock']))
    closed = numpy.array(
        [date2num(e.date.start)
         for e in events if e.eventclass == 'closed'])
    clock = numpy.array(
        [(date2num(e.date.start), date2num(e.date.end))
         for e in events if e.eventclass == 'clock'],
        dtype=[('start', float), ('end', float)])
    dh_closed = decompose_in_day_and_hour(closed)
    dh_clock_start = decompose_in_day_and_hour(clock['start'])
    dh_clock_end = decompose_in_day_and_hour(clock['end'])
    ax.plot(dh_closed['day'] + 0.5, dh_closed['hour'], 'x')
    if len(dh_clock_start) > 0:
        ax.errorbar(
            dh_clock_start['day'] + 0.5,
            (dh_clock_start['hour'] + dh_clock_start['hour']) / 2.0,
            yerr=(dh_clock_end['hour'] - dh_clock_start['hour']),
            fmt=None)
    set_xaxis_format_date(ax)
    ax.set_yticks([0, 6, 12, 18, 24])
    ax.set_ylim(24.1, -0.1)


def gene_clocked_and_closed(orgnodes, done='THIS IS DUMMY ARG', **kwds):
    """
    Plot punchcard-like clocked/closed activity.
    """
    fig = pylab.figure(figsize=FIGSIZE)
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    plot_clocked_and_closed(ax, orgnodes, **kwds)
    return fig


def gene_overview(orgnodes, done, days=30):
    """
    Draw graph from org file: overview
    """
    fig = pylab.figure(figsize=FIGSIZE)
    fig.subplots_adjust(bottom=0.2)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    plot_done_par_day(ax1, orgnodes, done, days, ylabel='Tasks/day [#]')
    plot_clocked_per_day(ax2, orgnodes, days, ylabel='Clocked/day [h]')
    ## ax1.set_yticks(ax1.get_yticks()[1:])
    ## ax2.set_yticks(ax2.get_yticks()[:-1])
    set_xaxis_format_date(ax1)
    pylab.setp(ax1.get_xticklabels(), visible=False)
    set_xaxis_format_date(ax2)
    # make xlim the same
    (xmin1, xmax1) = ax1.get_xlim()
    (xmin2, xmax2) = ax2.get_xlim()
    xlim = (min(xmin1, xmin2), max(xmax1, xmax2))
    ax1.set_xlim(xlim)
    ax2.set_xlim(xlim)
    #
    ax1.set_title('Overview')
    return fig


graph_func_map = {
    'done_par_day': gene_done_par_day,
    'clocked_par_day': gene_clocked_par_day,
    'tags_dist': gene_tags_dist,
    'clocked_and_closed': gene_clocked_and_closed,
    'overview': gene_overview,
    }
"""
A map between graph name to graph generator

A graph generator takes the following two parameters:

orgnodes
    a list of Orgnodes such as the list returned by orgparse.makelist.
done
    TODO tag for done. Usually, it is just 'DONE'.
"""
