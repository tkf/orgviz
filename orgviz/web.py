# -*- coding: utf-8 -*-

from flask import (Flask, request, json, render_template, send_from_directory,
                   url_for, redirect)
from werkzeug.contrib.cache import SimpleCache

import itertools
import os
import hashlib
import orgparse

from orgviz.graphs import (gene_clocked_par_day, gene_done_par_day,
                              gene_overview)
from orgviz.cal import gene_events
from orgviz.timeline import gene_timeline


app = Flask('orgviz')
app.config.from_object('orgviz.default_config')
cache = SimpleCache(default_timeout=60 * 60 * 24)


def get_orgnodes(filename):
    """Cached version of orgparse.makelist"""
    cachename_orgnodes = u'org:{0}'.format(filename)         # file path
    cachename_lastmtime = u'org_mtime:{0}'.format(filename)  # modified time
    orgnodes = cache.get(cachename_orgnodes)
    lastmtime = cache.get(cachename_lastmtime)
    mtime = os.path.getmtime(filename)
    if (not app.config['ORG_USE_CACHE'] or
        None in (orgnodes, lastmtime) or
        mtime > lastmtime):
        app.logger.debug("re-load org file '{0}'".format(filename))
        orgnodes = list(orgparse.load(filename)[1:])
        if app.config['ORG_USE_CACHE']:
            try:
                cache.set(cachename_orgnodes, orgnodes)
                cache.set(cachename_lastmtime, mtime)
            except RuntimeError as e:
                app.logger.error(
                    'Error while loading {0}.  Probably it is too big.\n'
                    'Got: {1}'.format(filename, e))
    else:
        app.logger.debug("use cache for org file '{0}'".format(filename))
    return orgnodes


def args_to_str(*args, **kwds):
    """
    Convert arguments and keyword arguments to readable string.

    >>> args_to_str(1, 2)
    '1, 2'
    >>> args_to_str(1, 2, a=3)
    '1, 2, a=3'
    >>> args_to_str(a=3)
    'a=3'

    """
    str_args = ', '.join(map(repr, args))
    str_kwds = ', '.join(map(
        lambda x: '{0}={1}'.format(x[0], repr(x[1])),
        kwds.iteritems()))
    return ', '.join(a for a in [str_args, str_kwds] if a)


def older_than(target_path, compare_list, getmtime=os.path.getmtime):
    """
    Which is old: target_path or an element (a path) in compare_list?

    It returns iterative to compare modified time of target_path and
    each path in compare_list.

    >>> def getmt(c):
    ...     return getmt.data[c]
    ...
    >>> getmt.data = dict(a=0, b=1, c=2, d=3, e=4)
    >>> all(older_than('a', 'bcd', getmtime=getmt))
    True
    >>> all(older_than('b', 'bcd', getmtime=getmt))
    False
    >>> all(older_than('c', 'bcd', getmtime=getmt))
    False
    >>> any(older_than('c', 'bcd', getmtime=getmt))
    True
    >>> any(older_than('d', 'bcd', getmtime=getmt))
    False
    >>> any(older_than('e', 'bcd', getmtime=getmt))
    False

    """
    target_mtime = getmtime(target_path)
    return (target_mtime < getmtime(c) for c in compare_list)


def get_graph(name, orgpaths, *args, **kwds):
    """
    Generates graph image and returns a file name

    If the generated cache file is newer than the any of its dependent
    org files, the graph will not be generated and the cache file will
    be used.

    """
    figname = u'{0}({1})'.format(
        name, args_to_str(*((orgpaths,) + args), **kwds))
    filename = '{0}.png'.format(
        hashlib.md5(figname.encode('utf-8')).hexdigest())
    filepath = os.path.join(app.config['CACHE_DIR'], filename)
    if (not app.config['ORG_USE_CACHE'] or
        not os.path.exists(filepath) or
        any(older_than(filepath, orgpaths))):
        app.logger.debug(
            "re-generate graph figname='{0}'".format(figname))
        orgnodeslist = orgnodes_from_paths(orgpaths)
        graph_func_map[name](orgnodeslist, *args, **kwds).savefig(filepath)
    else:
        app.logger.debug(
            "use cached graph figname='{0}'".format(figname))
    return filename


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


def orgnodes_from_paths(path_list):
    """
    Returns concatenated list of orgparse from list of path.
    """
    return reduce(lambda x, y: x + y, map(get_orgnodes, path_list))


def listjsonify(listdata):
    # Use json.dumps directly can be harmful, but it is easiest way
    # to do it, since fullcalendar only supports raw-array json feed.
    # see also:
    # - http://flask.pocoo.org/docs/security/#json-security
    # - https://github.com/mitsuhiko/flask/issues/170
    return json.dumps(listdata)


@app.route('/events_data')
def events_data():
    start = request.args.get('start')
    end = request.args.get('end')
    start = int(start) if start.isdigit() else None
    end = int(end) if end.isdigit() else None
    if request.args.get('eventclass'):  # is not None or ''
        eventclass = request.args['eventclass'].split(',')
    else:
        eventclass = ['deadline', 'scheduled']
    if request.args.get('eventfilter'):  # is not None or ''
        eventfilter = [
            app.config['ORG_CAL_FILTERS'][int(i)][1] for i in
            request.args['eventfilter'].split(',')]
    else:
        eventfilter = []
    classifier = app.config['ORG_CAL_EVENT_CLASSIFIER']
    orgpath_list = app.config['ORG_FILE_COMMON'] + app.config['ORG_FILE_CAL']
    orgnodes = orgnodes_from_paths(orgpath_list)
    events = gene_events(
        orgnodes,
        eventclass=eventclass, filters=eventfilter, classifier=classifier,
        start=start, end=end)
    return listjsonify(events)


def gene_get_static_file_under(parent):
    def timeglider_get_file(path):
        return url_for('static', filename=os.path.join(parent, path))
    return timeglider_get_file

tg_get_file = dict(
    css=gene_get_static_file_under('lib/timeglider/css'),
    js=gene_get_static_file_under('lib/timeglider/js'),
    tg=gene_get_static_file_under('lib/timeglider/js/timeglider'),
    )


@app.route('/orgviz')
def page_orgviz():
    eventfilters = [
        (i, name)
        for (i, (name, func)) in
        zip(itertools.count(), app.config['ORG_CAL_FILTERS'])
        ]
    eventfilters_name_to_id = dict((name, i) for (i, name) in eventfilters)

    def filter_name_to_id(dct):
        if 'filter' in dct:
            newdct = dct.copy()
            newdct['filter'] = [
                eventfilters_name_to_id[f] for f in dct['filter']]
            return newdct
        else:
            return dct
    cal_perspectives = [
        (i, name) for (i, (name, dct)) in
        zip(itertools.count(), app.config['ORG_CAL_PERSPECTIVES'])]
    cal_perspectives_data = dict(
        (i, filter_name_to_id(dct))
        for ((i, name), (_, dct)) in
        zip(cal_perspectives, app.config['ORG_CAL_PERSPECTIVES'])
        )
    return render_template(
        "orgviz.html",
        eventfilters=eventfilters,
        cal_perspectives=cal_perspectives,
        cal_perspectives_data=cal_perspectives_data,
        )


@app.route('/timeline/')
def page_timeline():
    return render_template("timeline.html", title='Time line', **tg_get_file)


@app.route('/timeline/<path:filepath>')
def page_timeline_file(filepath):
    """Redirect anything timeglider needs to its root directory"""
    return redirect(
        url_for(
            'static', filename=os.path.join('lib', 'timeglider', filepath)))


@app.route('/timeline_data')
def timeline_data():
    orgpath_list = app.config['ORG_FILE_TIMELINE']
    orgnodes_list = map(get_orgnodes, orgpath_list)
    initial_zoom = app.config['ORG_TIMELINE_INITIAL_ZOOM']
    return listjsonify(gene_timeline(
        orgnodes_list, orgpath_list, initial_zoom))


@app.route('/')
def index():
    return render_template("index.html", title='Top')


@app.route('/cal')
def cal():
    return render_template("cal.html", title='Calendar')


@app.route('/dones')
def dones():
    from orgviz.dones import get_data
    orgpath_list = app.config['ORG_FILE_COMMON'] + app.config['ORG_FILE_DONES']
    orgnodes_list = map(get_orgnodes, orgpath_list)
    return render_template(
        "dones.html",
        **get_data(orgnodes_list, orgpath_list, 'DONE'))


@app.route('/dones_data')
def dones_data():
    from orgviz.dones import get_data
    orgpath_list = app.config['ORG_FILE_COMMON'] + app.config['ORG_FILE_DONES']
    orgnodes_list = map(get_orgnodes, orgpath_list)
    return render_template(
        "dones_data.html",
        **get_data(orgnodes_list, orgpath_list, 'DONE'))


@app.route('/graphs')
def graphs():
    return render_template("graphs.html", title='Graphs')


@app.route('/graphs/<name>.png')
def graphs_image(name):
    filename = get_graph(
        name,
        app.config['ORG_FILE_COMMON'] + app.config['ORG_FILE_GRAPHS'],
        'DONE')
    return send_from_directory(app.config['CACHE_DIR'], filename)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='NEOrg - Numerical Experiment Organizer')

    parser.add_argument(
        '--conf', help='configuration file')
    parser.add_argument(
        '--debug', action='store_true', default=False)
    parser.add_argument(
        '--profile',
        help='path to store the profiled stats')
    parser.add_argument(
        '--profile-sort-by', nargs='+', default=('time', 'calls'),
        help='columns to sort the result by.')
    parser.add_argument(
        '--org-common', nargs='+',
        help='org files which is common to all pages')
    parser.add_argument(
        '--org-cal', nargs='+',
        help='additional org files for calendar')
    parser.add_argument(
        '--org-dones', nargs='+',
        help='additional org files for dones')
    parser.add_argument(
        '--org-graphs', nargs='+',
        help='additional org files for graphs')
    parser.add_argument(
        '--org-timeline', nargs='+',
        help='org files for timeline')
    parser.add_argument(
        '-t', '--tag', action='append')
    parser.add_argument(
        '--cache-dir', default='/tmp/orgviz')
    parser.add_argument(
        '--no-cache', default=False, action='store_true')
    parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='port to listen (default: %(default)s)')

    args = parser.parse_args()

    if args.conf:
        app.config.from_pyfile(args.conf)

    def update_if_specified(key, val):
        if val:
            app.config[key] = val

    app.config['DEBUG'] = args.debug
    update_if_specified('ORG_FILE_COMMON', args.org_common)
    update_if_specified('ORG_FILE_CAL', args.org_cal)
    update_if_specified('ORG_FILE_DONES', args.org_dones)
    update_if_specified('ORG_FILE_GRAPHS', args.org_graphs)
    update_if_specified('ORG_FILE_TIMELINE', args.org_timeline)
    update_if_specified('ORG_TAGS', args.tag)
    app.config['CACHE_DIR'] = cache_dir = args.cache_dir
    app.config['ORG_USE_CACHE'] = not args.no_cache

    for key in app.config:
        if key.startswith('ORG_FILE_'):
            app.config[key] = [
                os.path.expanduser(fpath) for fpath in app.config[key]]

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if args.profile:
        # hoock ProfilerMiddleware
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            file(args.profile, 'w'),
            args.profile_sort_by)

    app.run(port=args.port, extra_files=args.conf and [args.conf])


if __name__ == "__main__":
    main()
