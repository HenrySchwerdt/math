"""Convenience operations for the PI: start/finish bounded agent tasks and normalize sources.

These wrap the existing ledger primitives (research.new, task_state.update) so a task and its
RUN are created, filled and activated in one step, and closed consistently. They never change
mathematical proof status.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

import research as r
from task_state import update

URL = re.compile(r'https?://[^\s,;)]+')


def _now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _git(*args):
    try:
        return subprocess.check_output(['git', *args], cwd=r.ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _resolve_ref(project, ref):
    """Expand a unique short ID prefix (e.g. HYP-23351e75) to the full record ID."""
    if len(ref) >= 40:
        return ref
    matches = sorted({p.stem for p in r.project(project).rglob(f'{ref}*.json')
                      if re.fullmatch(r'[A-Z]+-[0-9a-f-]{36}', p.stem)})
    if len(matches) != 1:
        raise ValueError(f'Reference {ref!r} matches {len(matches)} records; give the full ID')
    return matches[0]


def start(project, title, question, role, model, refs=(), owned=(), resource=None,
          rationale=None, success=(), notes=None):
    """Create a TSK and its RUN, fill both, and mark the task active. Returns (key, tsk, run)."""
    tsk = r.new(project, 'TSK')
    run = r.new(project, 'RUN')
    refs = [_resolve_ref(project, x) for x in refs]
    hyps = [x for x in refs if x.startswith('HYP-')]
    run_id = run.stem
    t = json.loads(tsk.read_text())
    t.update(title=title, question=question, rationale=rationale or 'Selected by the PI.',
             refs=refs, success_criteria=list(success) or ['Exact statements; reproducible evidence; honest negatives.'],
             owned_files=[f'research/{project}/runs/{run_id}.md', f'research/{project}/runs/{run_id}.json', *owned],
             resource_limit=resource or 'One bounded subagent; no recursion; no commits.',
             next_action='Execute.', notes=notes or 'Created via research.py start.')
    r.write_json(tsk, t)
    d = json.loads(run.read_text())
    d.update(title=title, status='active', question=question,
             rationale=f'Bounded run for {tsk.stem}', refs=[tsk.stem, *refs],
             notes=f'Configured model {model}; runtime identity of subagents is not exposed to the PI.')
    d['run'].update(started_at=_now(), provider='anthropic', model=f'{model} (configured)', role=role,
                    task=tsk.stem, input_hypotheses=hyps, starting_commit=_git('rev-parse', 'HEAD'),
                    branch=_git('rev-parse', '--abbrev-ref', 'HEAD') or 'unknown',
                    worktree='shared checkout; exclusive ownership of listed files',
                    benchmark='See report', machine='See report')
    r.write_json(run, d)
    base = r.project(project)
    key = update(base, tsk.stem, run_id, 'active', f'Bounded {role} run started')['task_key']
    return key, tsk.stem, run_id


def finish(project, run_id, outcome, reason, next_action=None, files=(), commit=None):
    """Complete the RUN's task via the CLI state machine, then close the RUN.

    `commit` is the commit containing the run's work (default: HEAD). Call after committing the work.
    """
    path, d = r.load_run(project, run_id)
    if d['status'] != 'active':
        raise ValueError('finish requires an active run')
    base = r.project(project)
    result = update(base, d['run']['task'], run_id, 'completed', reason, outcome, next_action)
    d = json.loads(path.read_text())
    commit = commit or _git('rev-parse', 'HEAD')
    if not commit:
        raise ValueError('Cannot determine resulting commit')
    d['status'] = 'completed'
    d['outcome'] = outcome
    d['run']['completed_at'] = _now()
    d['run']['resulting_commit'] = commit
    if files:
        d['run']['files_changed'] = sorted(set(d['run']['files_changed']) | set(files))
    r.write_json(path, d)
    return result


def fix_sources(path):
    """Convert string sources to schema objects; URL-less strings move to notes. Returns (kept, moved)."""
    path = Path(path)
    d = json.loads(path.read_text())
    kept, moved = [], []
    for s in d.get('sources', []):
        if isinstance(s, dict):
            if s.get('url'):
                kept.append(s)
            else:
                moved.append(f"{s.get('title', '')} ({s.get('locator') or 'no locator'})")
            continue
        m = URL.search(s)
        if m:
            kept.append(dict(title=s.replace(m.group(0), '').strip(' ,;') or m.group(0),
                             url=m.group(0).rstrip('.'), retrieved_at=_now(),
                             locator='Agent-supplied bibliographic string (normalized by research.py fix-sources)'))
        else:
            moved.append(s)
    d['sources'] = kept
    if moved:
        d['notes'] = (d.get('notes') or '') + ' | Sources without URL (not schema sources): ' + ' || '.join(moved)
    r.write_json(path, d)
    return len(kept), len(moved)
