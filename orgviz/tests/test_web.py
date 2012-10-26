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


class TestWebEventsData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        cls.org_file = os.path.join(cls.tmpdir, 'test.org')
        web.app.config['ORG_FILE_COMMON'] = [cls.org_file]
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

    def get_events_data(self, start, end):
        start = totimestamp(datetime.datetime(*start))
        end = totimestamp(datetime.datetime(*end))
        rv = self.app.get(
            '/events_data?start={0:.0f}&end={1:.0f}'.format(start, end))
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
