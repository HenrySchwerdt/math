"""PI helper operations: start/finish tasks and normalize sources."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research as r
import lab_ops

SOURCE = r.ROOT


class LabOpsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / 'research/_templates', self.root / 'research/_templates')
        self.patcher = patch.object(r, 'ROOT', self.root)
        self.patcher.start()
        self.git = patch.object(lab_ops, '_git', return_value='a' * 40)
        self.git.start()
        r.init('example')

    def tearDown(self):
        self.git.stop()
        self.patcher.stop()
        self.temp.cleanup()

    def test_start_creates_filled_active_task_and_run(self):
        key, tsk, run = lab_ops.start('example', 'Title', 'Question?', 'experimenter', 'model-x',
                                      refs=['HYP-00000000-0000-0000-0000-000000000000'], owned=['x/'])
        t = json.loads((self.root / f'research/example/tasks/{tsk}.json').read_text())
        d = json.loads((self.root / f'research/example/runs/{run}.json').read_text())
        self.assertEqual(key, 'EXAMPLE-1')
        self.assertEqual(t['status'], 'active')
        self.assertIn('x/', t['owned_files'])
        self.assertEqual(d['status'], 'active')
        self.assertEqual(d['run']['task'], tsk)
        self.assertEqual(d['run']['role'], 'experimenter')
        self.assertEqual(d['run']['input_hypotheses'], ['HYP-00000000-0000-0000-0000-000000000000'])

    def test_start_expands_short_refs(self):
        hyp = r.new('example', 'HYP').stem
        _, _, run = lab_ops.start('example', 'T', 'Q', 'r', 'm', refs=[hyp[:12]])
        d = json.loads((self.root / f'research/example/runs/{run}.json').read_text())
        self.assertEqual(d['run']['input_hypotheses'], [hyp])
        with self.assertRaisesRegex(ValueError, 'matches 0'):
            lab_ops.start('example', 'T', 'Q', 'r', 'm', refs=['HYP-ffffffff'])

    def test_finish_completes_task_and_closes_run(self):
        key, tsk, run = lab_ops.start('example', 'T', 'Q', 'r', 'm')
        lab_ops.finish('example', run, 'verified', 'Done', 'Next', files=['f.txt'])
        t = json.loads((self.root / f'research/example/tasks/{tsk}.json').read_text())
        d = json.loads((self.root / f'research/example/runs/{run}.json').read_text())
        self.assertEqual((t['status'], t['outcome']), ('completed', 'verified'))
        self.assertEqual(d['status'], 'completed')
        self.assertEqual(d['run']['resulting_commit'], 'a' * 40)
        self.assertIn('f.txt', d['run']['files_changed'])
        with self.assertRaisesRegex(ValueError, 'active run'):
            lab_ops.finish('example', run, 'verified', 'Again')

    def test_fix_sources_normalizes_strings(self):
        p = r.new('example', 'RUN')
        d = json.loads(p.read_text())
        d['sources'] = ['A. Author, Title, Venue 2000, https://doi.org/10.1/x.', 'Unverified recollection',
                        {'title': 'Memory cite', 'url': None, 'retrieved_at': None, 'locator': 'sec 2'}]
        r.write_json(p, d)
        self.assertEqual(lab_ops.fix_sources(p), (1, 2))
        d = json.loads(p.read_text())
        self.assertEqual(d['sources'][0]['url'], 'https://doi.org/10.1/x')
        self.assertIn('Unverified recollection', d['notes'])
        self.assertIn('Memory cite (sec 2)', d['notes'])


if __name__ == '__main__':
    unittest.main()
