# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
"""
OrgViz - Browser based app to view org-mode files from different directions
===========================================================================

.. warning:: Work in progress.

In OrgViz, you can...

* View org-mode files in different formats:
  calendar / table / histogram

* Use rich formatting of web browsers but everything is reachable from
  keyboard.

* Write complex filter settings in Python.


Links
-----

* `Documentation (at Read the Docs) <http://orgviz.readthedocs.org/>`_
* `Repository (at GitHub) <https://github.com/tkf/orgviz>`_
* `Issue tracker (at GitHub) <https://github.com/tkf/orgviz/issues>`_
* `PyPI <http://pypi.python.org/pypi/orgviz>`_
* `Travis CI <https://travis-ci.org/#!/tkf/orgviz>`_ |build-status|

.. |build-status|
   image:: https://secure.travis-ci.org/tkf/orgviz.png?branch=master
   :target: http://travis-ci.org/tkf/orgviz
   :alt: Build Status


Install
-------

Installing OrgViz is as easy as::

   pip install orgviz  # or
   easy_install orgviz

If you want to draw graphs, install matplotlib_.


Usage
-----

Use the following command to start OrgViz server and the open
http://127.0.0.1:8000 in your browser::

   orgviz serve --port 8000 --conf YOUR/CONF/PATH.py

If you want to reload server automatically when you rewrite the
configuration file, currently you need to add ``--debug`` option::

   orgviz serve --debug [OTHER OPTIONS]

To quickly checkout what OrgViz can do, simply do::

   orgviz sample

This will make a configuration file and a randomly generated org file
in ``./sample/`` directory and start OrgViz server with them.  You can
edit the generated org file and see what happens to the pages in
OrgViz.


Configuration
^^^^^^^^^^^^^

Here is a minimal configuration.::

    ORG_COMMON_FILES = [
        'PATH/TO/ORG/FILE-1.org',
        'PATH/TO/ORG/FILE-2.org',
        # and more...
    ]

For more options available, see ``orgviz/default_config.py``.


Development
-----------

To run from source, use the following commands.  You need
coffee_, wget, unzip, make and git commands.  Also, all the
dependencies (see below) must be importable.::

   git clone git://github.com/tkf/orgviz.git
   cd orgviz
   make build
   python -m orgviz.cli serve [OPTIONS]

To run automated testing, run the following command.
You need the tox_ command line tool::

   make test


Dependencies
------------

- orgparse_
- Flask_
- argparse_ (Python <= 2.6)

Optional dependencies:

- matplotlib_

Dependencies for build and test include:

- coffee_
- tox_

.. _Flask: http://flask.pocoo.org/
.. _orgparse: https://github.com/tkf/orgparse
.. _argparse: http://code.google.com/p/argparse/
.. _matplotlib: http://matplotlib.org/
.. _coffee: http://coffeescript.org/
.. _tox: http://tox.testrun.org/


License
-------

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

"""
# [[[end]]]

__version__ = '0.0.1.dev1'
__author__ = 'Takafumi Arakaki'
__license__ = "MIT License"
