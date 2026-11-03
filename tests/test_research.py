"""Regression tests for provenance and cross-clone task exclusion."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research as r

SOURCE = r.ROOT


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        shutil.copytree(SOURCE / 'research/_templates', self.root / 'research/_templates')
        self.root_patch = patch.object(r, 'ROOT', self.root)
        self.root_patch.start()
        r.init('test-project')
        r.git('init', '-b', 'main')
        r.git('config', 'user.email', 'test@example.invalid')
        r.git('config', 'user.name', 'Test fixture')
        r.git('add', '.')
        r.git('commit', '-m', 'Test baseline')

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    def active_run(self):
        task = r.new('test-project', 'TSK').stem
        path = r.new('test-project', 'RUN')
        d = json.loads(path.read_text())
        d['status'] = 'active'
        d['run'].update(task=task, started_at=r.utc(), provider='test', model='fixture')
        r.write_json(path, d)
        return task, path

    def test_all_generated_drafts_validate(self):
        for kind in r.KINDS:
            r.new('test-project', kind)
        with contextlib.redirect_stdout(io.StringIO()):
            r.validate()

    def test_missing_reference_and_external_evidence_rejected(self):
        path = r.new('test-project', 'HYP')
        d = json.loads(path.read_text())
        d['refs'] = ['HYP-missing']
        r.write_json(path, d)
        with self.assertRaisesRegex(ValueError, 'missing artifact'):
            r.validate()
        d['refs'] = []
        d['evidence'] = ['../outside']
        r.write_json(path, d)
        with self.assertRaisesRegex(ValueError, 'Non-portable'):
            r.validate()

    def test_launch_failure_and_nonzero_exit_have_evidence(self):
        _, path = self.active_run()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(r.execute('test-project', path.stem,
                                         ['/definitely/missing/executable']), 0)
            self.assertEqual(r.execute('test-project', path.stem,
                                       [sys.executable, '-c', 'print("failure"); raise SystemExit(7)']), 7)
        d = json.loads(path.read_text())
        self.assertEqual(len(d['run']['commands']), 2)
        logs = [json.loads((self.root / p).read_text()) for p in d['run']['commands']]
        self.assertIn('error', logs[0])
        self.assertEqual(logs[1]['exit_code'], 7)
        self.assertIn('failure', logs[1]['output'])

    def test_timeout_is_preserved(self):
        _, path = self.active_run()
        with patch.object(r.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['x'], 300)):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(r.execute('test-project', path.stem, ['x']), 124)
        log = json.loads((self.root / json.loads(path.read_text())['evidence'][0]).read_text())
        self.assertIsNone(log['exit_code'])
        self.assertIn('Timed out', log['error'])

    def test_remote_claim_exclusion_and_completed_owner_release(self):
        remote = Path(self.temp.name) / 'origin.git'
        subprocess.run(['git', 'init', '--bare', str(remote)], check=True, capture_output=True)
        r.git('remote', 'add', 'origin', str(remote))
        task, first = self.active_run()
        second = r.new('test-project', 'RUN')
        d = json.loads(second.read_text())
        d['status'] = 'active'
        d['run']['task'] = task
        r.write_json(second, d)
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            r.claim('test-project', task, first.stem)
        claim_hash = captured.getvalue().strip()
        # Independent checkout shares only the remote ownership authority.
        clone = Path(self.temp.name) / 'second'
        subprocess.run(['git', 'clone', str(remote), str(clone)], check=True, capture_output=True)
        shutil.copytree(self.root / 'research', clone / 'research')
        with patch.object(r, 'ROOT', clone):
            r.git('config', 'user.email', 'test@example.invalid')
            r.git('config', 'user.name', 'Second fixture')
            with self.assertRaises(subprocess.CalledProcessError):
                r.claim('test-project', task, second.stem)
        with self.assertRaisesRegex(ValueError, 'another run'):
            r.claim('test-project', task, second.stem, claim_hash)
        d = json.loads(first.read_text())
        d['status'] = 'completed'
        r.write_json(first, d)
        r.claim('test-project', task, first.stem, claim_hash)
        self.assertEqual(r.git('ls-remote', 'origin', f'refs/heads/claims/{task}'), '')

    def test_local_path_redaction(self):
        self.assertEqual(r.sanitize('/Users/private/file'), '<local-path>')
        self.assertEqual(r.sanitize('/home/private/file'), '<local-path>')
        self.assertEqual(r.sanitize(str(self.root) + '/input'), '<repo>/input')


class ConfigurationTests(unittest.TestCase):
    def test_provider_role_parity(self):
        config = tomllib.loads((SOURCE / '.codex/config.toml').read_text())
        self.assertEqual(config['model'], 'gpt-6.1-sol')
        for role in (SOURCE / 'docs/roles').glob('*.md'):
            codex = tomllib.loads((SOURCE / '.codex/agents' / (role.stem + '.toml')).read_text())
            claude = (SOURCE / '.claude/agents' / (role.stem + '.md')).read_text()
            expected = 'gpt-6.1-sol' if role.stem in ('principal-investigator', 'final-reviewer', 'independent-reviewer') else 'gpt-6-luna'
            self.assertEqual(codex['model'], expected)
            self.assertIn(f'docs/roles/{role.name}', codex['developer_instructions'])
            self.assertIn(f'docs/roles/{role.name}', claude)
            self.assertTrue(claude.startswith('---\nname: ' + role.stem + '\n'))
            self.assertIn('model: claude-' + ('opus' if expected == 'gpt-6.1-sol' else 'sonnet') + '-5-5\n', claude)


if __name__ == '__main__':
    unittest.main()
