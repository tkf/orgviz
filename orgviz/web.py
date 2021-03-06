# -*- coding: utf-8 -*-

import itertools
import os
from io import BytesIO

from flask import (Flask, request, json, render_template, send_file,
                   url_for, redirect, jsonify)
from werkzeug.contrib.cache import SimpleCache

import orgparse


app = Flask('orgviz')
app.config.from_object('orgviz.default_config')
cache = SimpleCache(default_timeout=60 * 60 * 24)


def get_cache(cachename, compute, mtime):
    """
    Generic cache function based on time stamp.
    """
    cachename_value = u'cache:{0}'.format(cachename)
    cachename_lastmtime = u'mtime:{0}'.format(cachename)
    value = cache.get(cachename_value)
    lastmtime = cache.get(cachename_lastmtime)
    if (not app.config['ORG_USE_CACHE'] or
        None in (value, lastmtime) or
        mtime > lastmtime):
        app.logger.debug("re-compute '{0}'".format(cachename))
        value = compute()
        if app.config['ORG_USE_CACHE']:
            try:
                cache.set(cachename_value, value)
                cache.set(cachename_lastmtime, mtime)
            except RuntimeError as e:
                app.logger.error(
                    'Error while caching {0}.  Probably it is too big.\n'
                    'Got: {1}'.format(cachename, e))
    else:
        app.logger.debug("use cache for '{0}'".format(cachename))
    return value


def orgnodes_from_paths(path_list):
    """
    Returns concatenated list of orgparse from list of path.
    """
    return reduce(lambda x, y: x + y, map(get_orgnodes, path_list))


def get_orgnodes(filename):
    """Cached version of `orgparse.load`."""
    return get_cache(
        'org:{0}'.format(filename),
        lambda: list(orgparse.load(filename)[1:]),
        os.path.getmtime(filename))


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


def listjsonify(listdata):
    # Use json.dumps directly can be harmful, but it is easiest way
    # to do it, since fullcalendar only supports raw-array json feed.
    # see also:
    # - http://flask.pocoo.org/docs/security/#json-security
    # - https://github.com/mitsuhiko/flask/issues/170
    return json.dumps(listdata)


# ----------------------------------------------------------------------- #
# Main

@app.route('/')
def index():
    return redirect(url_for('page_orgviz'))


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
    cal_eventclasses = \
        zip(['deadline', 'scheduled', 'closed', 'clock']
            + app.config['ORG_CAL_ADD_EVENTCLASSES'] + ['none'],
            itertools.chain('zxcvbnm', itertools.repeat('')))
    return render_template(
        "orgviz.html",
        eventfilters=eventfilters,
        cal_perspectives=cal_perspectives,
        cal_perspectives_data=cal_perspectives_data,
        cal_eventclasses=cal_eventclasses,
        graphs=[
            ('clocked_par_day', 'Clocked time per day'),
            ('done_par_day', 'Tasks done par day'),
            ('tags_dist', 'Top 10 tags in closed tasks'),
            ('clocked_and_closed', 'Clocked and closed activities'),
        ],
        )


# ----------------------------------------------------------------------- #
# Calendar

@app.route('/events_data')
def events_data():
    from .cal import gene_events
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
    orgpaths = app.config['ORG_COMMON_FILES'] + app.config['ORG_CAL_FILES']
    orgnodes = orgnodes_from_paths(orgpaths)
    events = gene_events(
        orgnodes,
        eventclass=eventclass, filters=eventfilter, classifier=classifier,
        start=start, end=end)
    return listjsonify(events)


@app.route('/cal_config')
def cal_config():
    return jsonify(dict(
        eventSources=app.config['ORG_CAL_ADD_EVENTSOURCES'],
    ))


# ----------------------------------------------------------------------- #
# Dones

@app.route('/dones_data')
def dones_data():
    from .dones import get_data
    orgpaths = app.config['ORG_COMMON_FILES'] + app.config['ORG_DONES_FILES']
    orgnodes_list = map(get_orgnodes, orgpaths)
    return render_template(
        "dones_data.html",
        **get_data(orgnodes_list, orgpaths, 'DONE'))


# ----------------------------------------------------------------------- #
# Graph

def get_graph(name, orgpaths, *args, **kwds):
    """
    Generates graph image and returns a file name

    If the generated cache file is newer than the any of its dependent
    org files, the graph will not be generated and the cache file will
    be used.

    """
    def generate_graph():
        from .graphs import graph_func_map
        image = BytesIO()
        orgnodes = orgnodes_from_paths(orgpaths)
        graph_func_map[name](orgnodes, *args, **kwds).savefig(image)
        image.seek(0)
        return image.getvalue()
    image = get_cache(
        'graph:{0}({1})'.format(name, args_to_str(orgpaths, *args, **kwds)),
        generate_graph,
        max(os.path.getmtime, orgpaths))
    return BytesIO(image)


@app.route('/graphs/<name>.png')
def graphs_image(name):
    return send_file(
        get_graph(
            name,
            app.config['ORG_COMMON_FILES'] + app.config['ORG_GRAPHS_FILES'],
            'DONE'),
        attachment_filename='{0}.png'.format(name))


# ----------------------------------------------------------------------- #
# Timeline

@app.route('/timeline/')
def page_timeline():
    return render_template("timeline.html", title='Time line')


@app.route('/timeline/__history__.html')
def page_timeline_history():
    """
    Dummy page for Simile Widgets.

    See: `Exhibit/Template history .html - SIMILE Widgets
    <http://simile-widgets.org/wiki/Exhibit/Template_history_.html>`_
    """
    return "<html><body></body></html>"


@app.route('/timeline_data')
def timeline_data():
    from .timeline import gene_timeline
    return listjsonify(gene_timeline(orgnodes_from_paths(
        app.config['ORG_COMMON_FILES'] + app.config['ORG_TIMELINE_FILES'])))


# ----------------------------------------------------------------------- #
# CLI

def add_arguments(parser):
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
        '--no-cache', default=False, action='store_true')
    parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='port to listen (default: %(default)s)')


def run(conf=None, debug=False, no_cache=False,
        profile=None, profile_sort_by=None, port=8000):
    """
    Start orgviz webserver.
    """
    if conf:
        app.config.from_pyfile(os.path.abspath(conf))

    def update_if_specified(key, val):
        if val:
            app.config[key] = val

    app.config['DEBUG'] = debug
    app.config['ORG_USE_CACHE'] = not no_cache

    for key in app.config:
        if key.startswith('ORG_') and key.endswith('_FILES'):
            app.config[key] = [
                os.path.expanduser(fpath) for fpath in app.config[key]]

    if profile:
        # hook ProfilerMiddleware
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            file(profile, 'w'),
            profile_sort_by)

    app.run(port=port, extra_files=conf and [conf])


command = ('serve', add_arguments, run)
