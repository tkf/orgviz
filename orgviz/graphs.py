"""
Generate graphs from org files to visualize how you manage tasks
"""

import matplotlib
matplotlib.use('Agg')
import pylab
import numpy
from matplotlib.dates import date2num
from datetime import datetime

from orgparse.date import total_minutes

from orgviz.dones import find_rootname

## timezone = matplotlib.dates.pytz.timezone('Europe/Paris')
## xa_formatter = matplotlib.dates.DateFormatter("%b %d %H:%M", timezone)
## #xa_locator = matplotlib.dates.HourLocator(tz=timezone)
## xa_locator = matplotlib.dates.AutoDateLocator(timezone)
## xa_formatter = matplotlib.dates.AutoDateFormatter(xa_locator, timezone)

from matplotlib.dates import  DateFormatter, WeekdayLocator, \
     DayLocator, MONDAY  # , HourLocator

mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()                  # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # Eg, Jan 12
dayFormatter = DateFormatter('%d')      # Eg, 12
# See:
# http://matplotlib.sourceforge.net/examples/pylab_examples/finance_demo.html

DTYPE_TABLE = [
    ('closed', float), ('scheduled', float),
    ('clock', int), ('estimate', int),
    ('rootid', int),
    ]


def gene_get_row():
    """
    Generate get_row and id2rootname.

    get_row
        Get row from org node. Each row shold have data which is specified
        by DTYPE_TABLE.

    id2rootname
        Dictionary for id-rootname correspondence which will be stored
        if you run ``get_row(node)`` for node with unknown 'rootname'.
    """
    id2rootname = {0: ''}
    rootname2id = {'': 0}

    def get_row(node):
        closed = node.closed
        scheduled = node.scheduled
        closed = (closed and date2num(closed.start)) or 0
        scheduled = (scheduled and date2num(scheduled.start)) or 0
        clock = node.clock
        clock = (clock and
                 # Check: is using minute correct?
                 sum([total_minutes(c.duration) for c in clock])) or 0
        estimate = node.get_property('Estimate') or 0
        # find rootid
        rootid = 0
        rootname = find_rootname(node)
        if rootname:
            if rootname in rootname2id:
                rootid = rootname2id[rootname]
            else:
                rootid = max(id2rootname) + 1
                id2rootname[rootid] = rootname
                rootname2id[rootname] = rootid
        return (closed, scheduled, clock, estimate, rootid)
    return (get_row, id2rootname)


def get_table(orgnodes, done):
    """
    Get table from org files
    """
    (get_row, id2rootname) = gene_get_row()
    row_list = [
        get_row(node)
        for node in orgnodes
        if node.todo == done
        ]
    table = numpy.array(row_list, dtype=DTYPE_TABLE)
    table.sort(order='closed')
    return (table, id2rootname)


def set_xaxis_format_date(ax):
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    ## ax.xaxis.set_major_formatter(xa_formatter)
    ## ax.xaxis.set_major_locator(xa_locator)
    pylab.setp(ax.get_xticklabels(), rotation=40, ha="right")


def plot_clocked_per_day(ax, orgnodes, done, days,
                         ylabel='Clocked Time Per Day [h]'):
    (table, id2rootname) = get_table(orgnodes, done)
    closed = table['closed']
    if len(closed) == 0:
        return
    lastday = int(numpy.floor(closed[-1]))
    firstday = lastday - days + 1
    i0 = ((closed - firstday) ** 2).argmin()

    dates = numpy.arange(days)
    cpd = numpy.zeros(days, dtype='float')  # clocked per day
    closed0_int = numpy.floor(closed[i0:]).astype(int)
    table0 = table[i0:]
    for i in dates:
        cpd[i] = numpy.extract(closed0_int == firstday + i,
                               table0['clock']).sum()
    ax.bar(dates + firstday, cpd / 60.0, width=1, color='b', alpha=0.3)
    ax.set_ylabel(ylabel)


def gene_clocked_par_day(orgnodes, done, days=30):
    """
    Draw graph from org files: clocked task par day
    """
    fig = pylab.figure(figsize=(5, 4))
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    plot_clocked_per_day(ax, orgnodes, done, days)
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
    today = int(date2num(datetime.now())) + 1  # end of today
    start = today - days
    time_array = time_array_closed(orgnodes, done, start)
    ax.hist(time_array, bins=days, range=(start, today),
            color='b', alpha=0.3)
    ax.set_ylabel(ylabel)


def gene_done_par_day(orgnodes, done, days=30):
    """
    Draw graph from org file: done (closed) task par day
    """
    fig = pylab.figure(figsize=(5, 4))
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    plot_done_par_day(ax, orgnodes, done, days)
    set_xaxis_format_date(ax)
    return fig


def gene_overview(orgnodes, done, days=30):
    """
    Draw graph from org file: overview
    """
    fig = pylab.figure(figsize=(5, 4))
    fig.subplots_adjust(bottom=0.2)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    plot_done_par_day(ax1, orgnodes, done, days, ylabel='Tasks/day [#]')
    plot_clocked_per_day(ax2, orgnodes, done, days, ylabel='Clocked/day [h]')
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
