"""Public notebook projection and evidence-label regression tests."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research as r
from research_site import generate, repository_url, report

SOURCE = r.ROOT
COMMIT = 'a' * 40
REPO = 'https://github.com/example/research'


class NotebookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(SOURCE / 'research/_templates', self.root / 'research/_templates')
        self.patcher = patch.object(r, 'ROOT', self.root)
        self.patcher.start()
        r.init('example')
        self.task = r.new('example', 'TSK')
        self.run = r.new('example', 'RUN')
        d = json.loads(self.run.read_text())
        d.update(title='Successful infrastructure check', status='completed', outcome='verified')
        d['run'].update(task=self.task.stem, completed_at='2026-11-03T07:00:00Z',
                        tests=['Observed test output'], commands=['private/not-published.evidence'])
        r.write_json(self.run, d)

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def test_projection_has_tasks_results_and_commit_specific_sources(self):
        data = generate(self.root, REPO, COMMIT)
        self.assertEqual(len(data['records']), 2)
        self.assertEqual(data['projects'][0]['open_tasks'], 1)
        self.assertEqual(data['projects'][0]['formally_verified'], 0)
        results = (self.root / 'website/research/results.md').read_text()
        self.assertIn('Successful infrastructure check', results)
        self.assertIn('not-applicable', results)
        self.assertIn('## Formally verified research\n\n_No records yet._', results)
        detail = (self.root / f'website/research/records/{self.run.stem}.md').read_text()
        self.assertIn(f'{REPO}/blob/{COMMIT}/', detail)
        self.assertIn(f'../records/{self.task.stem}.md', detail)
        self.assertIn('Observed test output', detail)
        self.assertIn('Task completion and run outcomes are not proof certificates', detail)

    def test_summary_never_bundles_raw_commands_or_private_fields(self):
        (self.root / 'research/example/private').mkdir()
        (self.root / 'research/example/private/secret.txt').write_text('DO_NOT_PUBLISH')
        data = generate(self.root, REPO, COMMIT)
        encoded = json.dumps(data)
        self.assertNotIn('DO_NOT_PUBLISH', encoded)
        self.assertNotIn('not-published.evidence', encoded)
        self.assertNotIn('commands', encoded)

    def test_research_content_is_inert_inside_vue_pre_wrapper(self):
        d = json.loads(self.task.read_text())
        d['title'] = '{{ danger() }} <script>alert(1)</script>'
        r.write_json(self.task, d)
        self.task.with_suffix('.md').write_text('<script>alert(1)</script>\n{{ danger() }}\n</div>')
        generate(self.root, REPO, COMMIT)
        content = (self.root / f'website/research/records/{self.task.stem}.md').read_text()
        self.assertIn('<div v-pre>', content)
        self.assertNotIn('<script>', content.split('---', 2)[2])
        self.assertIn('&lt;script&gt;', content)
        self.assertEqual(content.count('</div>'), 1)

    def test_code_examples_keep_exact_display_characters(self):
        rendered = report('```c\n#include <stdio.h>\n```\nInline `<tag>`')
        self.assertIn('#include &lt;stdio.h&gt;', rendered)
        self.assertNotIn('&amp;lt;', rendered)
        self.assertIn('<code>&lt;tag&gt;</code>', rendered)

    def test_unresolved_results_and_dirty_previews_are_explicit(self):
        d = json.loads(self.task.read_text())
        d['outcome'] = 'unresolved'
        r.write_json(self.task, d)
        data = generate(self.root, REPO, COMMIT, dirty=True)
        self.assertTrue(data['dirty'])
        results = (self.root / 'website/research/results.md').read_text()
        self.assertIn(self.task.stem, results.split('## Blocked and unresolved work')[1])
        self.assertIn('uncommitted changes', (self.root / 'website/research/index.md').read_text())

    def test_citations_link_primary_sources_with_retrieval_and_locator(self):
        d = json.loads(self.task.read_text())
        d['sources'] = [{'title': 'Primary source', 'url': 'https://example.org/paper',
                         'retrieved_at': '2026-11-03T07:00:00Z', 'locator': 'Theorem 2'}]
        r.write_json(self.task, d)
        generate(self.root, REPO, COMMIT)
        detail = (self.root / f'website/research/records/{self.task.stem}.md').read_text()
        self.assertIn('[Primary source](https://example.org/paper)', detail)
        self.assertIn('Theorem 2; retrieved 2026-11-03T07:00:00Z', detail)

    def test_regeneration_removes_stale_generated_pages(self):
        generate(self.root, REPO, COMMIT)
        stale = self.root / 'website/research/stale.md'
        stale.write_text('Obsolete')
        generate(self.root, REPO, COMMIT)
        self.assertFalse(stale.exists())

    def test_refuses_to_replace_authored_content(self):
        target = self.root / 'website/research'
        target.mkdir(parents=True)
        original = target / 'authored.md'
        original.write_text('Keep this')
        with self.assertRaisesRegex(ValueError, 'not owned'):
            generate(self.root, REPO, COMMIT)
        self.assertEqual(original.read_text(), 'Keep this')

    def test_only_safe_github_repository_urls_and_commits(self):
        self.assertEqual(repository_url('git@github.com:example/research.git'), REPO)
        for bad in ('javascript:alert(1)', 'https://github.com/example/research?x=1',
                    'https://evil.invalid/example/research', 'https://secret@github.com/example/research'):
            with self.assertRaises(ValueError):
                repository_url(bad)
        with self.assertRaisesRegex(ValueError, 'commit hash'):
            generate(self.root, REPO, '../main')


if __name__ == '__main__':
    unittest.main()
