import os
import tempfile
import shutil
import unittest
import textwrap
import json

from .. import web

TMP_PREFIX = 'orgviz-test-'


class TestWebEventsData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp(prefix=TMP_PREFIX)
        cls.org_file = os.path.join(cls.tmpdir, 'test.org')
        web.app.config['ORG_FILE_COMMON'] = [cls.org_file]
        web.app.config['ORG_FILE_CAL'] = []
        web.app.config['NO_CACHE'] = False
        cls.app = web.app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    def test_single_event(self):
        with open(self.org_file, 'w') as f:
            f.write(textwrap.dedent("""
            * Node title
              SCHEDULED: <2012-10-23 Tue>
            """))
        rv = self.app.get('/events_data?start=1349042400&end=1352674800')
        events_data = json.loads(rv.data)
        self.assertEqual(len(events_data), 1)
        self.assertEqual(events_data[0]['title'], 'Node title')
