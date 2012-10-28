import os

from .randomnodes import writeorg
from . import web


CONF_TEMPLATE = """\
ORG_COMMON_FILES = [{orgpath!r}]
"""


def add_arguments(parser):
    parser.add_argument('--num', default=40, type=int,
                        help='number of org nodes to generate')
    parser.add_argument('--pre-days', default=30, type=int,
                        help='time range (min) to generate random events in.')
    parser.add_argument('--post-days', default=30, type=int,
                        help='time range (max) to generate random events in.')
    parser.add_argument('--no-server', action='store_true',
                        help='do not run web server.  '
                        'just generate sample files.')
    parser.add_argument('directory', default='sample', nargs='?',
                        help='directory in which generate sample files')
    web.add_arguments(parser)


def run(directory, num, pre_days, post_days, no_server, **kwds):
    """
    Generate a random org file and start OrgViz server to show it.

    This is helpful to quickly try out OrgViz features.

    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    orgpath = os.path.join(directory, 'random.org')
    confpath = os.path.join(directory, 'conf.py')
    with open(orgpath, 'wt') as f:
        writeorg(f, num, pre_days=pre_days, post_days=post_days)
    with open(confpath, 'wt') as f:
        f.write(CONF_TEMPLATE.format(orgpath=orgpath))

    if not no_server:
        if not kwds['conf']:
            kwds['conf'] = confpath
        web.run(**kwds)


command = ('sample', add_arguments, run)
