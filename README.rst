OrgViz - Browser based app to view org-mode files from different directions
===========================================================================

|build-status|

.. warning:: Work in progress.

In OrgViz, you can...

* View org-mode files in different formats:
  calendar / table / histogram

* Use rich formatting of web browsers but everything is reachable from
  keyboard.

* Write complex filter settings in Python.


.. |build-status|
   image:: https://secure.travis-ci.org/tkf/orgviz.png?branch=master
   :target: http://travis-ci.org/tkf/orgviz
   :alt: Build Status


Dependencies
============

- orgparse_
- Flask_
- argparse_ (Python <= 2.6)

Optional dependencies:

- matplotlib_

.. _Flask: http://flask.pocoo.org/
.. _orgparse: https://github.com/tkf/orgparse
.. _argparse: http://code.google.com/p/argparse/
.. _matplotlib: http://matplotlib.org/


License
=======

OrgViz is licensed under the terms of the MIT license (see COPYING).

OrgViz bundles libraries with the following licenses.

- `jQuery`_ : MIT or GPL v2 license
- `FullCalendar`_ : MIT or GPL v2 license
- `jQuery Hotkeys`_ : MIT or GPL v2 license
- `ColorBox`_ : MIT license
- `Nuvola`_: LGPL v2.1

.. _jQuery: http://jquery.com/
.. _FullCalendar: http://arshaw.com/fullcalendar/
.. _jQuery Hotkeys: https://github.com/tzuryby/jquery.hotkeys
.. _ColorBox: http://jacklmoore.com/colorbox
.. _Nuvola: http://www.icon-king.com/projects/nuvola/
