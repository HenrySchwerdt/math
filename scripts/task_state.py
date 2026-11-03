"""Explicit task status updates with immutable, referenced transition evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from pathlib import Path
import tempfile
import uuid

from task_keys import load

STATUSES = ('open', 'active', 'blocked', 'completed')
OUTCOMES = ('verified', 'refuted', 'unresolved', 'blocked', 'inconclusive')


def _update(base, task_key, run_id, status, reason, outcome=None, next_action=None):
    base = Path(base)
    keys = load(base)['tasks']
    matches = [ident for ident, key in keys.items() if task_key in (ident, key)]
    if len(matches) != 1:
        raise ValueError('Unknown task ID or project task key')
    ident = matches[0]
    if not re.fullmatch(r'TSK-[0-9a-f-]{36}', ident):
        raise ValueError('Invalid canonical task ID')
    if not isinstance(run_id, str) or not re.fullmatch(r'RUN-[0-9a-f-]{36}', run_id):
        raise ValueError('Invalid run ID')
    task_path = base / 'tasks' / f'{ident}.json'
    run_path = base / 'runs' / f'{run_id}.json'
    if task_path.is_symlink() or run_path.is_symlink():
        raise ValueError('Task and run paths must not be symlinks')
    run = json.loads(run_path.read_text())
    if run['run']['task'] != ident or run['status'] != 'active':
        raise ValueError('Status updates require an active run assigned to the task')
    if status not in STATUSES or outcome is not None and outcome not in OUTCOMES:
        raise ValueError('Invalid task status or outcome')
    if next_action is not None and not next_action.strip():
        raise ValueError('Next action must not be blank')
    if not reason.strip():
        raise ValueError('A status-change reason is required')
    original = task_path.read_bytes()
    task = json.loads(original)
    before = {field: task[field] for field in ('status', 'outcome', 'next_action')}
    after = dict(before, status=status)
    if outcome is not None:
        after['outcome'] = outcome
    if next_action is not None:
        after['next_action'] = next_action
    if status == 'completed' and after['outcome'] is None:
        raise ValueError('A completed task needs an explicit outcome')
    if before == after:
        return {'task': ident, 'task_key': keys[ident], 'changed': False}
    events = base / 'events'
    if events.is_symlink():
        raise ValueError('Task event directory must not be a symlink')
    events.mkdir(exist_ok=True)
    event_id = f'EVT-{uuid.uuid4()}'
    event_path = events / f'{event_id}.evidence'
    relative = str(event_path.relative_to(base.parent.parent))
    task.update(after)
    task['evidence'].append(relative)
    task_data = (json.dumps(task, indent=2) + '\n').encode()
    event = dict(id=event_id, kind='task-status-change', task=ident, task_key=keys[ident],
                 timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                 run=run_id, actor={key: run['run'][key] for key in ('provider', 'model', 'role')},
                 before=before, after=after, reason=reason,
                 before_sha256=hashlib.sha256(original).hexdigest(),
                 after_sha256=hashlib.sha256(task_data).hexdigest())
    # Persist evidence first. Only events referenced by the atomic task snapshot
    # are treated as applied; a crash before replace leaves an unapplied orphan.
    with event_path.open('x') as output:
        output.write(json.dumps(event, indent=2) + '\n')
    fd, temporary = tempfile.mkstemp(prefix='.task-state-', dir=task_path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(task_data)
        if task_path.read_bytes() != original:
            raise ValueError('Task changed concurrently; update was not applied')
        os.replace(temporary, task_path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'task': ident, 'task_key': keys[ident], 'changed': True, 'event': relative}


def update(base, task_key, run_id, status, reason, outcome=None, next_action=None):
    base = Path(base)
    keys = load(base)['tasks']
    matches = [ident for ident, key in keys.items() if task_key in (ident, key)]
    if len(matches) != 1 or not re.fullmatch(r'TSK-[0-9a-f-]{36}', matches[0]):
        raise ValueError('Unknown or invalid task ID')
    lock = base / 'tasks' / (matches[0] + '.lock')
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError('Task update is already locked; inspect any interrupted run before removing a stale lock') from error
    os.close(descriptor)
    try:
        return _update(base, task_key, run_id, status, reason, outcome, next_action)
    finally:
        lock.unlink()
