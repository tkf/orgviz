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
ORG_CAL_EVENT_CLASSIFIER = None
ORG_CAL_ADD_EVENTCLASSES = []
ORG_CAL_ADD_EVENTSOURCES = []


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
