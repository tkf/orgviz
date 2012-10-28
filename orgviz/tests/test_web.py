import os
import tempfile
import shutil
import unittest
import textwrap
import json
import datetime

from .. import web
from ..cal import totimestamp

TMP_PREFIX = 'orgviz-test-'


def timestamp(*args, **kwds):
    return totimestamp(datetime.datetime(*args, **kwds))


class TestWebEventsData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        cls.org_file = os.path.join(cls.tmpdir, 'test.org')
        web.app.config['ORG_COMMON_FILES'] = [cls.org_file]
        cls.app = web.app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    def setUp(self):
        web.cache.clear()

    def write_org_file(self, text):
        with open(self.org_file, 'w') as f:
            f.write(textwrap.dedent(text))

    def test_single_event(self):
        self.write_org_file("""
        * Node title
          SCHEDULED: <2012-10-23 Tue>
        """)
        rv = self.app.get('/events_data?start=1349042400&end=1352674800')
        events_data = json.loads(rv.data)
        self.assertEqual(len(events_data), 1)
        self.assertEqual(events_data[0]['title'], 'Node title')

    def get_events_data(self, start, end, eventclass=None):
        start = totimestamp(datetime.datetime(*start))
        end = totimestamp(datetime.datetime(*end))
        url = '/events_data?start={0:.0f}&end={1:.0f}'.format(start, end)
        if eventclass:
            assert isinstance(eventclass, list)
            url += '&eventclass={0}'.format(','.join(eventclass))
        rv = self.app.get(url)
        return json.loads(rv.data)

    def test_start_end(self):
        self.write_org_file("""
        * Node 1
          SCHEDULED: <2012-10-21 Tue>
        * Node 2
          SCHEDULED: <2012-10-22 Wed>
        * Node 3
          SCHEDULED: <2012-10-24 Fri>
        """)
        # FIXME: clarify boundary condition 2012-10-23 in Node 3 does not work!
        data = self.get_events_data(start=(2012, 10, 20), end=(2012, 10, 23))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Node 1')
        self.assertEqual(data[1]['title'], 'Node 2')

    def test_scheduled_deadline_closed(self):
        self.write_org_file("""
            * Node 1
              """  # indent is important here
            # Following should go in one line:
            "CLOSED: [2012-10-24 Fri] "
            "SCHEDULED: <2012-10-21 Tue> "
            "DEADLINE: <2012-10-22 Wed>")
        data = self.get_events_data(
            start=(2012, 10, 1), end=(2012, 11, 1),
            eventclass=['deadline', 'scheduled', 'closed'])
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['title'], 'Node 1')
        self.assertEqual(data[1]['title'], 'Node 1')
        self.assertEqual(data[2]['title'], 'Node 1')

        actual_ts = set([data[i]['start'] for i in range(3)])
        desired_ts = set([timestamp(2012, 10, d) for d in [21, 22, 24]])
        self.assertEqual(actual_ts, desired_ts)

        actual_colors = set([data[i]['color'] for i in range(3)])
        desired_colors = set(['green', 'red', 'blue'])  # FIXME: don't hardcode
        self.assertEqual(actual_colors, desired_colors)

    def test_clock(self):
        self.write_org_file("""
        * Node 1
          CLOCK: [2012-10-26 Fri 17:20]--[2012-10-26 Fri 17:30] =>  0:10
          CLOCK: [2012-10-26 Fri 20:00]--[2012-10-26 Fri 20:10] =>  0:10
        * Node 2
          CLOCK: [2012-10-26 Fri 19:20]--[2012-10-26 Fri 19:30] =>  0:10
          SCHEDULED: <2012-10-27 Sat>
        * Node 3
          CLOCK: [2012-10-26 Fri 20:20]--[2012-10-26 Fri 20:30] =>  0:10
        """)
        data = self.get_events_data(
            start=(2012, 10, 1), end=(2012, 11, 1),
            eventclass=['clock'])
        self.assertEqual(
            [(d['start'], d['end']) for d in data],
            [(timestamp(2012, 10, 26, h1, m1),
              timestamp(2012, 10, 26, h2, m2))
             for (h1, m1, h2, m2) in [(17, 20, 17, 30),
                                      (20,  0, 20, 10),
                                      (19, 20, 19, 30),
                                      (20, 20, 20, 30)]])

    def check_page(self, page):
        rv = self.app.get(page)
        assert 'body' in rv.data

    def test_page_orgviz(self):
        self.check_page('/orgviz')

    def test_page_timeline(self):
        self.check_page('/timeline/')
