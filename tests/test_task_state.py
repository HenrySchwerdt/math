"""CLI task updates append history without changing proof status."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research as r
from task_state import update
from research_site import task_activity

SOURCE = r.ROOT


class TaskStateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        shutil.copytree(SOURCE/'research/_templates',self.root/'research/_templates')
        self.patcher=patch.object(r,'ROOT',self.root);self.patcher.start()
        r.init('example')
        self.base=self.root/'research/example'
        self.path=r.new('example','TSK')
        self.run=r.new('example','RUN')
        d=json.loads(self.run.read_text());d['status']='active';d['run'].update(task=self.path.stem,provider='test',model='fixture',role='test');r.write_json(self.run,d)

    def tearDown(self):
        self.patcher.stop();self.temp.cleanup()

    def test_status_change_updates_ledger_and_timeline(self):
        original=json.loads(self.path.read_text())
        result=update(self.base,'EXAMPLE-1',self.run.stem,'active','Starting the assigned task')
        task=json.loads(self.path.read_text());event=json.loads((self.root/result['event']).read_text())
        self.assertEqual(task['status'],'active')
        self.assertEqual(task['proof_status'],original['proof_status'])
        self.assertEqual(event['before']['status'],'open')
        self.assertEqual(event['after']['status'],'active')
        self.assertEqual(event['after_sha256'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertIn(result['event'],task['evidence'])
        self.assertTrue(any(e['kind']=='status' for e in task_activity(self.root,task,[],'https://github.com/example/research','a'*40)))
        unchanged=update(self.base,'EXAMPLE-1',self.run.stem,'active','Same request')
        self.assertFalse(unchanged['changed'])

    def test_completion_requires_outcome_and_assigned_active_run(self):
        with self.assertRaisesRegex(ValueError,'explicit outcome'):
            update(self.base,'EXAMPLE-1',self.run.stem,'completed','Done')
        result=update(self.base,self.path.stem,self.run.stem,'completed','Checks passed','verified','Continue next task')
        self.assertTrue(result['changed'])
        run=json.loads(self.run.read_text());run['status']='completed';r.write_json(self.run,run)
        with self.assertRaisesRegex(ValueError,'active run'):
            update(self.base,'EXAMPLE-1',self.run.stem,'active','Reopen')

    def test_concurrent_updates_are_rejected(self):
        lock=self.path.with_suffix('.lock');lock.touch()
        with self.assertRaisesRegex(ValueError,'already locked'):
            update(self.base,'EXAMPLE-1',self.run.stem,'active','Start')
        self.assertTrue(lock.exists())


if __name__=='__main__':
    unittest.main()
