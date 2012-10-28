"""
OrgViz configuration
====================

OrgViz configuration file is just a Python file.  Only the variables
in upper case will be loaded.

"""

# ----------------------------------------------------------------------- #
# Global configuration

ORG_USE_CACHE = True
"""
Use in-memory cache for org-mode files to improve response speed.
"""

ORG_COMMON_FILES = []
"""
Common org-mode files.

These files will be included in any view.

"""


# ----------------------------------------------------------------------- #
# Calendar

ORG_CAL_FILES = []
"""
Org-mode files to include calendar view.
"""

ORG_CAL_FILTERS = []
"""
List of (name, function)-pairs to specify events to show in calendar.

The first element of the tuple must be human readable name of filter
and the second element must be a callable object (function).  Each
function must take one :class:`orgviz.event.Event` object and return a
bool.

The order of the filters is reflected to the order in the web
interface.  That's why this option is specified as a list (association
list), instead of a dict.

"""

# FIXME: error occurs in JS when ORG_CAL_PERSPECTIVES is []
ORG_CAL_PERSPECTIVES = [
    ('month', {
        'event': ['deadline', 'scheduled'],
        'view': 'month',
        }),
    ('month all', {
        'event': ['deadline', 'scheduled', 'closed', 'clock', 'none'],
        'view': 'month',
        }),
]
"""
Calendar perspectives definitions.

To quickly switch events to include, calendar view and filters, you
can define perspectives.  Perspective is defined in the following
format::

   [('PERSPECTIVE NAME', {
        'event': ['deadline', 'scheduled', ...],  # closed/clock/none/...
        'view': 'month',  # or agendaWeek/basicWeek/agendaDay/basicDay
        'filter': ['FILTER 1', 'FILTER 2', ...],
        }),
    ...
    ]

See also:
`FullCalendar Documentation - Available Views
<http://arshaw.com/fullcalendar/docs/views/Available_Views/>`_

"""

ORG_CAL_EVENT_CLASSIFIER = None
"""
A function to define extra eventclass.

The following example defines 'home' event, depending on node tag::

    def ORG_CAL_EVENT_CLASSIFIER(event):
        if '@home' in event.tags:
            return 'home'

"""

ORG_CAL_ADD_EVENTCLASSES = []
"""
Extra eventclasses to consider.

Add eventclasses here if you defined `ORG_CAL_EVENT_CLASSIFIER`.

Example::

    ORG_CAL_ADD_EVENTCLASSES = ['home']

"""

ORG_CAL_ADD_EVENTSOURCES = []
"""
Extra event sources for FullCalendar.

This is useful for adding events from another servers, such as
holidays.  For example, to add Japanese holidays you can set it to::

   [{'url': (
        'https://www.google.com/calendar/feeds'
        '/japanese%40holiday.calendar.google.com/public/basic'),
     'color': '#AB8B00',
     'textColor': '#AB8B00',
     'backgroundColor': 'white',
    }]

- `FullCalendar Documentation - Google Calendar
  <http://arshaw.com/fullcalendar/docs/google_calendar/>`_

"""


# ----------------------------------------------------------------------- #
# Done list

ORG_DONES_FILES = []
"""
Org-mode files to include in done list view.
"""


# ----------------------------------------------------------------------- #
# Graph

ORG_GRAPHS_FILES = []
"""
Org-mode files to include in graph view.
"""


# ----------------------------------------------------------------------- #
# Timeline

ORG_TIMELINE_FILES = []
"""
Org-mode files to include in timeline view.
"""

ORG_TIMELINE_INITIAL_ZOOM = 30
