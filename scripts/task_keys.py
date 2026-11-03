"""Persistent, project-scoped display keys; canonical UUIDs remain unchanged."""
import json
from pathlib import Path
import re
import os
import tempfile


def load(base):
    path = Path(base) / 'TASKS.json'
    if not path.exists():
        return {'prefix': Path(base).name.upper(), 'tasks': {}}
    data = json.loads(path.read_text())
    if not re.fullmatch(r'[A-Z][A-Z0-9-]*', data['prefix']):
        raise ValueError('Invalid task-key prefix')
    keys = list(data['tasks'].values())
    if len(keys) != len(set(keys)) or any(not re.fullmatch(re.escape(data['prefix']) + r'-[1-9][0-9]*', key) for key in keys):
        raise ValueError('Duplicate or invalid project task key')
    return data


def register(base, prefix=None):
    """PI/integration operation: preserve existing keys and assign missing tasks."""
    base = Path(base)
    data = load(base)
    if prefix:
        if data['tasks'] and prefix != data['prefix']:
            raise ValueError('Cannot change a prefix after keys have been assigned')
        if not re.fullmatch(r'[A-Z][A-Z0-9-]*', prefix):
            raise ValueError('Invalid task-key prefix')
        data['prefix'] = prefix
    records = [json.loads(p.read_text()) for p in (base / 'tasks').glob('TSK-*.json')]
    next_number = max((int(k.rsplit('-', 1)[1]) for k in data['tasks'].values()), default=0) + 1
    for record in sorted(records, key=lambda d: (d['created_at'], d['id'])):
        if record['id'] not in data['tasks']:
            data['tasks'][record['id']] = f'{data["prefix"]}-{next_number}'
            next_number += 1
    # Write atomically; shared assignment is PI-owned, never a parallel worker edit.
    fd, name = tempfile.mkstemp(prefix='.task-keys-', dir=base)
    try:
        with os.fdopen(fd, 'w') as output:
            output.write(json.dumps(data, indent=2) + '\n')
        os.replace(name, base / 'TASKS.json')
    finally:
        Path(name).unlink(missing_ok=True)
    return data
