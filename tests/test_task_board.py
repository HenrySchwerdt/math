"""Persistent project task keys and evidence-driven task activity."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from task_keys import load, register
from research_site import task_activity


class TaskKeyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / 'project'
        (self.base / 'tasks').mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def task(self, name, date):
        (self.base / 'tasks' / f'TSK-{name}.json').write_text(json.dumps({'id': f'TSK-{name}', 'created_at': date}))

    def test_keys_remain_stable_when_older_task_is_imported(self):
        self.task('one', '2026-11-03T10:00:00Z')
        self.assertEqual(register(self.base, 'TEST')['tasks']['TSK-one'], 'TEST-1')
        self.task('older', '2020-01-01T00:00:00Z')
        data = register(self.base)
        self.assertEqual(data['tasks'], {'TSK-one': 'TEST-1', 'TSK-older': 'TEST-2'})
        self.assertEqual(register(self.base), data)
        with self.assertRaisesRegex(ValueError, 'Cannot change'):
            register(self.base, 'OTHER')

    def test_duplicate_or_invalid_keys_rejected(self):
        (self.base / 'TASKS.json').write_text(json.dumps({'prefix':'TEST', 'tasks':{'a':'TEST-1', 'b':'TEST-1'}}))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            load(self.base)


class TaskActivityTests(unittest.TestCase):
    def test_only_observed_steps_and_public_command_metadata_are_projected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / 'command.evidence'
            evidence.write_text(json.dumps({'argv':['python', 'test.py'], 'started_at':'2026-11-03T10:01:00Z', 'exit_code':0, 'output':'DO_NOT_BUNDLE_RAW_OUTPUT'}))
            task = {'id':'task', 'created_at':'2026-11-03T10:00:00Z', 'rationale':'Defined scope'}
            run = {'id':'run', 'type':'RUN', 'title':'Check toy case', 'outcome':'verified', 'run':{'task':'task', 'started_at':'2026-11-03T10:00:30Z','completed_at':'2026-11-03T10:02:00Z','role':'experimenter','provider':'test','model':'fixture','commands':['command.evidence'],'tests':['Observed success']}}
            events = task_activity(root, task, [run], 'https://github.com/example/research', 'a'*40)
            self.assertEqual([e['kind'] for e in events], ['created','run','command','outcome'])
            self.assertEqual(events[2]['argv'], ['python', 'test.py'])
            self.assertNotIn('DO_NOT_BUNDLE_RAW_OUTPUT', json.dumps(events))
            self.assertEqual(task_activity(root, task, [], 'https://github.com/example/research', 'a'*40)[0]['kind'], 'created')

    def test_invalid_command_metadata_is_rejected_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            evidence=root/'bad.evidence'
            task={'id':'task','created_at':'2026-11-03T10:00:00Z','rationale':'Scope'}
            run={'id':'run','type':'RUN','title':'Run','run':{'task':'task','commands':['bad.evidence']}}
            evidence.write_text(json.dumps({'argv':'python test.py','started_at':'2026-11-03T10:00:00Z'}))
            with self.assertRaisesRegex(ValueError,'bad.evidence: argv'):
                task_activity(root,task,[run],'https://github.com/example/research','a'*40)
            evidence.write_text(json.dumps({'argv':['python'],'started_at':'not-a-date'}))
            with self.assertRaisesRegex(ValueError,'bad.evidence: expected a valid UTC'):
                task_activity(root,task,[run],'https://github.com/example/research','a'*40)

    def test_review_creation_does_not_claim_decision_timestamp(self):
        task={'id':'task','created_at':'2026-11-03T10:00:00Z','rationale':'Scope'}
        review={'id':'review','type':'REV','created_at':'2026-11-03T10:01:00Z', 'status':'completed',
                'review':{'targets':['task'],'decision':'accept','rationale':'Bounded review'}}
        events=task_activity(Path('.'),task,[review],'https://github.com/example/research','a'*40)
        self.assertEqual(events[-1]['title'],'Review artifact created')
        self.assertIn('current decision: accept',events[-1]['detail'])

    def test_private_evidence_and_unrelated_runs_are_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            task={'id':'task','created_at':'2026-11-03T10:00:00Z','rationale':'Scope'}
            run={'id':'run','type':'RUN','title':'Unrelated','run':{'task':'other','commands':['does-not-exist']}}
            self.assertEqual(len(task_activity(Path(tmp), task, [run], 'https://github.com/example/research','a'*40)), 1)


if __name__ == '__main__':
    unittest.main()
