"""Package helpers: summary of ledger changes and local snapshots."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research as r
import package_ops

SOURCE = r.ROOT


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, check=True, text=True, capture_output=True).stdout.strip()


class PackageOpsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / 'research/_templates', self.root / 'research/_templates')
        git(self.root, 'init', '-q', '-b', 'main')
        git(self.root, 'config', 'user.email', 't@example.com')
        git(self.root, 'config', 'user.name', 'Test')
        self.patcher = patch.object(r, 'ROOT', self.root)
        self.patcher.start()
        r.init('example')
        git(self.root, 'add', '-A')
        git(self.root, 'commit', '-q', '-m', 'base')
        self.base = git(self.root, 'rev-parse', 'HEAD')

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def test_summary_lists_new_records_by_type(self):
        h = r.new('example', 'HYP')
        d = json.loads(h.read_text()); d['title'] = 'A precise conjecture'; r.write_json(h, d)
        git(self.root, 'add', '-A'); git(self.root, 'commit', '-q', '-m', 'hyp')
        text = package_ops.summary(self.base)
        self.assertIn('### Hypotheses (1)', text)
        self.assertIn('A precise conjecture', text)

    def test_snapshot_commits_without_push(self):
        (self.root / 'research/example/note.txt').write_text('wip')
        head = package_ops.snapshot('agents running', push=False)
        self.assertTrue(head)
        self.assertIn('WIP snapshot: agents running', git(self.root, 'log', '-1', '--format=%B'))
        self.assertIsNone(package_ops.snapshot('nothing new', push=False))


if __name__ == '__main__':
    unittest.main()
