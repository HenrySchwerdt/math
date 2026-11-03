"""Package lifecycle helpers: validate, summarize, snapshot and sync research packages.

A "package" is the set of commits on the research branch since the base (default origin/main)
that will be proposed as one pull request. Creating and merging the pull request itself is done
by the orchestrator's GitHub tool; see docs/WORKFLOW.md for the full protocol.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import research as r

TYPES = ('PRF', 'REV', 'HYP', 'TSK', 'PAP', 'DEC', 'RUN', 'EXP', 'ALG')


def _git(*args, cwd=None, check=True):
    return subprocess.run(['git', *args], cwd=cwd or r.ROOT, text=True, capture_output=True, check=check).stdout.strip()


def check(base='origin/main', lean=False):
    """Validate the COMMITTED state (HEAD) in a clean temporary worktree, ignoring uncommitted files."""
    head = _git('rev-parse', 'HEAD')
    tmp = Path(tempfile.mkdtemp(prefix='package-check-'))
    results = []
    try:
        _git('worktree', 'add', '--detach', '-q', str(tmp / 'wt'), head)
        wt = tmp / 'wt'
        lake = shutil.which('lake') or str(Path.home() / '.elan/bin/lake')
        steps = [('ledger check', [sys.executable, 'scripts/research.py', 'check']),
                 ('site build', [sys.executable, 'scripts/research.py', 'site']),
                 ('unit tests', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'])]
        if lean:
            lake_dir = r.ROOT / '.lake'
            if lake_dir.exists() and not (wt / '.lake').exists():
                (wt / '.lake').symlink_to(lake_dir)
            steps.append(('lake build', [lake, 'build']))
        for name, cmd in steps:
            p = subprocess.run(cmd, cwd=wt, text=True, capture_output=True)
            results.append((name, p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:] or ['']))
    finally:
        _git('worktree', 'remove', '--force', str(tmp / 'wt'), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
    ahead = _git('rev-list', '--count', f'{base}..HEAD', check=False) or '?'
    return head, ahead, results


def summary(base='origin/main'):
    """Markdown summary of ledger records added or changed in base..HEAD, grouped by type."""
    files = _git('diff', '--name-only', f'{base}...HEAD').splitlines()
    groups = {t: [] for t in TYPES}
    other = set()
    for f in files:
        p = r.ROOT / f
        if f.startswith('research/') and f.endswith('.json') and p.is_file():
            try:
                d = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            if isinstance(d, dict) and d.get('type') in groups:
                groups[d['type']].append(d)
                continue
        if not f.startswith('research/'):
            other.add(f.split('/')[0] if '/' in f else f)
    lines = [f'## Ledger changes since `{base}`', '']
    labels = dict(PRF='Formal proofs', REV='Reviews', HYP='Hypotheses', TSK='Tasks', PAP='Papers',
                  DEC='Decisions', EXP='Experiments', ALG='Algorithms', RUN='Runs')
    for t in TYPES:
        if t == 'RUN' or not groups[t]:
            continue
        lines.append(f'### {labels[t]} ({len(groups[t])})')
        for d in sorted(groups[t], key=lambda x: x['id']):
            status = '/'.join(str(x) for x in (d.get('proof_status'), d.get('outcome')) if x)
            lines.append(f'- `{d["id"][:12]}` {d["title"]} — {status}')
        lines.append('')
    if groups['RUN']:
        lines.append(f'Runs touched: {len(groups["RUN"])}.')
    if other:
        lines.append('Non-ledger paths changed: ' + ', '.join(sorted(other)) + '.')
    lines.append('')
    lines.append('No improvement on known ECDLP complexity is claimed unless a record above states measured or proved evidence.')
    return '\n'.join(lines)


def snapshot(message, push=True, paths=('research',)):
    """Commit all current changes under `paths` as a labelled WIP snapshot (and push unless push=False)."""
    _git('add', '-A', *paths)
    if not _git('diff', '--cached', '--name-only'):
        return None
    trailer = os.environ.get('RESEARCH_COMMIT_TRAILER', '').replace('\\n', '\n')
    body = f'WIP snapshot: {message}\n\nUnreviewed in-progress work; superseded when the owning runs finish.'
    _git('commit', '-q', '-m', body + (f'\n\n{trailer}' if trailer else ''))
    head = _git('rev-parse', '--short', 'HEAD')
    if push:
        branch = _git('rev-parse', '--abbrev-ref', 'HEAD')
        _git('push', '-q', 'origin', branch)
    return head


def sync(base_branch='main'):
    """Fetch and merge the base branch into the current branch (merge commit, never rebase)."""
    _git('fetch', '-q', 'origin', base_branch)
    _git('merge', '-q', '--no-edit', f'origin/{base_branch}')
    return _git('rev-parse', '--short', 'HEAD')
