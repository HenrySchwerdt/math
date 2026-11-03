#!/usr/bin/env python3
"""Small shared file ledger; no model calls or autonomous scheduling."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
KINDS = dict(TSK='tasks', HYP='hypotheses', EXP='experiments', ALG='algorithms',
             PRF='proofs', REV='reviews', RUN='runs', DEC='decisions', PAP='papers')


def utc():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def git(*args, input=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True, input=input).strip()


def project(name):
    if not re.fullmatch(r'[a-z][a-z0-9-]*', name):
        raise ValueError('Project must be a lowercase slug')
    return ROOT / 'research' / name


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def init(name):
    base = project(name)
    base.mkdir(exist_ok=False)
    for directory in KINDS.values():
        (base / directory).mkdir()
        (base / directory / '.gitkeep').touch()
    for filename in ('STATUS.md', 'BACKLOG.md'):
        (base / filename).write_text(f'# {name} — {filename[:-3]}\n\n'
                                    'No research results yet. Define the first task.\n')


def new(name, kind):
    base = project(name)
    ident = f'{kind}-{uuid.uuid4()}'
    d = dict(id=ident, type=kind, title='Draft — define before work', created_at=utc(),
             status='open', question='Unassigned; define exact question',
             rationale='Unassigned; record why selected', assumptions=[], sources=[],
             refs=[], evidence=[], claims=[], proof_status='not-applicable', outcome=None,
             next_action='Fill draft metadata and report before execution',
             notes='Draft only; no execution or verification claimed.')
    if kind == 'TSK':
        d.update(success_criteria=['Define measurable completion criteria'],
                 owned_files=[], resource_limit='No workers or experiments authorized yet')
    if kind == 'RUN':
        d['run'] = dict(started_at=None, completed_at=None, provider='unassigned',
                        model='unassigned', role='unassigned', task=None,
                        input_hypotheses=[], starting_commit=None, branch='unassigned',
                        worktree='unassigned', commands=[], files_changed=[],
                        resulting_commit=None, tests=[], benchmark='Not recorded',
                        machine='Not recorded', reviews=[])
    if kind == 'REV':
        d['review'] = dict(run=None, target_commit=None, targets=[],
                           decision='revise', rationale='Review not performed',
                           counterexamples=['Not attempted'], complexity='Not reviewed',
                           limitations='Draft review, not an assessment',
                           initial_packet='Not supplied')
    path = base / KINDS[kind] / f'{ident}.json'
    write_json(path, d)
    path.with_suffix('.md').write_text((ROOT / 'research/_templates/report.md').read_text()
                                      .replace('ID — title', ident + ' — draft'))
    if kind == 'TSK':
        from task_keys import register
        register(base)
    return path


def records(name=None):
    paths = (project(name).glob('*/*.json') if name else
             (ROOT / 'research').glob('*/*/*.json'))
    return [(p, json.loads(p.read_text())) for p in sorted(paths)]


def links(d):
    r = d.get('run', {})
    v = d.get('review', {})
    return set(d['refs'] + r.get('input_hypotheses', []) + r.get('reviews', [])
               + v.get('targets', []) + [x for x in
                 [d.get('task'), r.get('task'), v.get('run')] if x])


def local(path):
    p = Path(path)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError(f'Non-portable path: {path}')
    target = (ROOT / p).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
        raise ValueError(f'Missing or external evidence: {path}')


def validate():
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads((ROOT / 'research/_templates/artifact.schema.json').read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    rows = records()
    ids = [d['id'] for _, d in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate artifact IDs')
    for path, d in rows:
        validator.validate(d)
        if not d['id'].startswith(d['type'] + '-') or path.stem != d['id']:
            raise ValueError(f'ID/type/path mismatch: {path.name}')
        if path.parent.name != KINDS[d['type']]:
            raise ValueError(f'Wrong directory: {path.name}')
        if not path.with_suffix('.md').is_file():
            raise ValueError(f'Missing report: {path.name}')
        for ref in links(d):
            if ref not in ids:
                raise ValueError(f'{d["id"]}: missing artifact {ref}')
        for evidence in d['evidence'] + d.get('run', {}).get('commands', []):
            local(evidence)
        if d['status'] == 'completed' and d['outcome'] is None:
            raise ValueError('Completed artifact needs outcome')
        if d['type'] == 'RUN':
            r = d['run']
            if d['status'] in ('active', 'completed'):
                if not r['started_at'] or r['provider'] == 'unassigned' or r['model'] == 'unassigned':
                    raise ValueError('Started run needs actual time/provider/model')
            if d['status'] == 'completed' and (not r['completed_at'] or not r['resulting_commit']):
                raise ValueError('Completed run needs end time and resulting commit')
            if r['completed_at'] and (not r['started_at'] or r['completed_at'] < r['started_at']):
                raise ValueError('Invalid run time order')
            for field in ('starting_commit', 'resulting_commit'):
                if r[field]:
                    git('cat-file', '-e', r[field] + '^{commit}')
            for command in r['commands']:
                # Only research.py exec evidence (JSON objects) may be listed as commands;
                # the public site generator parses each entry.
                if not command.endswith('.evidence') or not isinstance(json.loads((ROOT / command).read_text()), dict):
                    raise ValueError(f'{d["id"]}: run.commands must list exec .evidence files only: {command}')
        if d['type'] == 'REV' and d['status'] == 'completed':
            git('cat-file', '-e', d['review']['target_commit'] + '^{commit}')
        if d['proof_status'] == 'formally-verified':
            for field in ('lean_file', 'toolchain_file', 'build_evidence'):
                local(d['formal'][field])
            git('cat-file', '-e', d['formal']['source_commit'] + '^{commit}')
    from task_keys import load
    for base in (ROOT / 'research').iterdir():
        if (base / 'TASKS.json').exists():
            index = load(base)
            project_ids = {d['id'] for p, d in rows if p.parent.parent == base and d['type'] == 'TSK'}
            if set(index['tasks']) != project_ids:
                raise ValueError(f'{base.name}: task-key registry must cover exactly the project tasks')
    print(f'Validated {len(rows)} research records')


def audit(name, hypothesis=None):
    rows = records(name)
    selected = {hypothesis} if hypothesis else {d['id'] for _, d in rows}
    if hypothesis and hypothesis not in {d['id'] for _, d in rows}:
        raise ValueError('Unknown hypothesis')
    while hypothesis:
        expanded = selected | {d['id'] for _, d in rows if links(d) & selected}
        expanded |= set().union(*(links(d) for _, d in rows if d['id'] in selected))
        if expanded == selected:
            break
        selected = expanded
    for path, d in sorted(rows, key=lambda row: (row[1]['created_at'], row[1]['id'])):
        if d['id'] in selected:
            print(f'{d["created_at"]} {d["id"]} {d["status"]}/{d["outcome"]}: {d["title"]}')
            print(f'  {path.relative_to(ROOT)} | next: {d["next_action"]}')


def load_run(name, ident):
    if not re.fullmatch(r'RUN-[0-9a-f-]{36}', ident):
        raise ValueError('Invalid run ID')
    path = project(name) / 'runs' / f'{ident}.json'
    return path, json.loads(path.read_text())


def claim(name, task, run_id, expected=None):
    _, d = load_run(name, run_id)
    if not re.fullmatch(r'TSK-[0-9a-f-]{36}', task):
        raise ValueError('Invalid task ID')
    if not (project(name) / 'tasks' / f'{task}.json').is_file():
        raise ValueError('Task not found')
    if d['run']['task'] != task or (not expected and d['status'] != 'active'):
        raise ValueError('Run must own task; acquisition requires active status')
    ref = f'refs/heads/claims/{task}'
    if expected:
        if not re.fullmatch(r'[0-9a-f]{40,64}', expected):
            raise ValueError('Expected a claim commit hash')
        git('fetch', 'origin', ref)
        if git('rev-parse', 'FETCH_HEAD') != expected:
            raise ValueError('Remote claim changed')
        owner = json.loads(git('show', f'{expected}:claim.json'))
        if owner['run'] != run_id or owner['project'] != name or owner['task'] != task:
            raise ValueError('Claim belongs to another run/task/project')
        git('push', f'--force-with-lease={ref}:{expected}', 'origin', f':{ref}')
        return
    owner = dict(project=name, task=task, run=run_id, acquired_at=utc(),
                 provider=d['run']['provider'], model=d['run']['model'])
    blob = git('hash-object', '-w', '--stdin', input=json.dumps(owner))
    tree = git('mktree', input=f'100644 blob {blob}\tclaim.json\n')
    commit = git('commit-tree', tree, input=f'Exclusive claim {task}\n')
    git('push', f'--force-with-lease={ref}:', 'origin', f'{commit}:{ref}')
    print(commit)


def sanitize(text):
    text = text.replace(str(ROOT), '<repo>')
    text = text.replace(tempfile.gettempdir(), '<temp>')
    return re.sub(r"/(?:Users|home)/[^\s\"']+", '<local-path>', text)


def execute(name, run_id, argv):
    if argv and argv[0] == '--':
        argv = argv[1:]
    if not argv:
        raise ValueError('Command is required')
    path, d = load_run(name, run_id)
    if d['status'] != 'active':
        raise ValueError('Only active runs can execute commands')
    log = dict(argv=[sanitize(arg) for arg in argv], cwd='.', started_at=utc())
    # A temporary file avoids accumulating arbitrary child output in memory.
    with tempfile.TemporaryFile() as output:
        try:
            result = subprocess.run(argv, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                    timeout=300, check=False)
            log['exit_code'] = result.returncode
        except subprocess.TimeoutExpired:
            log['exit_code'] = None
            log['error'] = 'Timed out after 300 seconds'
        except OSError as error:
            log['exit_code'] = None
            log['error'] = sanitize(str(error))
        log['completed_at'] = utc()
        output.seek(0)
        raw = output.read(65537)
    log['truncated'] = len(raw) > 65536
    text = raw[:65536].decode('utf-8', errors='replace')
    text = sanitize(text)
    log['output'] = text
    target = path.parent / f'{run_id}-command-{uuid.uuid4()}.evidence'
    write_json(target, log)
    rel = str(target.relative_to(ROOT))
    d['run']['commands'].append(rel)
    d['evidence'].append(rel)
    write_json(path, d)
    print(rel)
    return log['exit_code'] if log['exit_code'] is not None else 124


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check')
    sub.add_parser('site', help='Generate the public VitePress notebook from the ledger')
    key_parser = sub.add_parser('task-keys', help='Assign missing readable task keys (PI/integration only)')
    key_parser.add_argument('project')
    key_parser.add_argument('--prefix')
    task_parser = sub.add_parser('task', help='Update task status and record the transition')
    task_parser.add_argument('project')
    task_parser.add_argument('task')
    task_parser.add_argument('--run', required=True)
    task_parser.add_argument('--status', required=True, choices=['open', 'active', 'blocked', 'completed'])
    task_parser.add_argument('--reason', required=True)
    task_parser.add_argument('--outcome', choices=['verified', 'refuted', 'unresolved', 'blocked', 'inconclusive'])
    task_parser.add_argument('--next-action')
    start_parser = sub.add_parser('start', help='Create, fill and activate a TSK with its RUN (PI helper)')
    start_parser.add_argument('project')
    start_parser.add_argument('--title', required=True)
    start_parser.add_argument('--question', required=True)
    start_parser.add_argument('--role', required=True)
    start_parser.add_argument('--model', required=True)
    start_parser.add_argument('--refs', nargs='*', default=[])
    start_parser.add_argument('--owned', nargs='*', default=[])
    start_parser.add_argument('--resource')
    start_parser.add_argument('--rationale')
    finish_parser = sub.add_parser('finish', help='Complete a RUN and its task after the work is committed')
    finish_parser.add_argument('project')
    finish_parser.add_argument('run')
    finish_parser.add_argument('--outcome', required=True, choices=['verified', 'refuted', 'unresolved', 'blocked', 'inconclusive'])
    finish_parser.add_argument('--reason', required=True)
    finish_parser.add_argument('--next-action')
    finish_parser.add_argument('--files', nargs='*', default=[])
    finish_parser.add_argument('--commit')
    fix_parser = sub.add_parser('fix-sources', help='Normalize string sources in a record to schema objects')
    fix_parser.add_argument('paths', nargs='+')
    rm = sub.add_parser('render-md', help='Fill untouched template .md reports from their JSON records')
    rm.add_argument('project')
    pc = sub.add_parser('package-check', help='Validate the committed HEAD in a clean worktree (ignores uncommitted agent files)')
    pc.add_argument('--base', default='origin/main')
    pc.add_argument('--lean', action='store_true', help='also run lake build')
    ps = sub.add_parser('package-summary', help='Markdown PR summary of ledger changes since base')
    ps.add_argument('--base', default='origin/main')
    sn = sub.add_parser('snapshot', help='WIP-commit research changes; use --no-push while a PR is open')
    sn.add_argument('message')
    sn.add_argument('--no-push', action='store_true')
    sy = sub.add_parser('sync-main', help='After a merge: fetch and merge origin/main into the current branch')
    sy.add_argument('--base-branch', default='main')
    for cmd in ('init', 'new', 'audit', 'claim', 'release', 'exec'):
        p = sub.add_parser(cmd)
        p.add_argument('project')
        if cmd == 'new':
            p.add_argument('kind', choices=KINDS)
        if cmd == 'audit':
            p.add_argument('--hypothesis')
        if cmd in ('claim', 'release'):
            p.add_argument('task')
        if cmd in ('claim', 'release', 'exec'):
            p.add_argument('run')
        if cmd == 'release':
            p.add_argument('expected')
        if cmd == 'exec':
            p.add_argument('argv', nargs=argparse.REMAINDER)
    a = parser.parse_args()
    if a.command == 'check':
        validate()
    elif a.command == 'task':
        from task_state import update
        print(json.dumps(update(project(a.project), a.task, a.run, a.status, a.reason, a.outcome, a.next_action), indent=2))
    elif a.command == 'start':
        from lab_ops import start
        key, tsk, run = start(a.project, a.title, a.question, a.role, a.model, a.refs, a.owned, a.resource, a.rationale)
        print(json.dumps(dict(task_key=key, task=tsk, run=run), indent=2))
    elif a.command == 'finish':
        from lab_ops import finish
        print(json.dumps(finish(a.project, a.run, a.outcome, a.reason, a.next_action, a.files, a.commit), indent=2))
    elif a.command == 'package-check':
        from package_ops import check as pcheck
        head, ahead, results = pcheck(a.base, a.lean)
        print(f'HEAD {head} ({ahead} commits ahead of {a.base})')
        for name, code, tail in results:
            print(f'  {"OK  " if code == 0 else "FAIL"} {name}: {tail[0]}')
        return 0 if all(code == 0 for _, code, _ in results) else 1
    elif a.command == 'package-summary':
        from package_ops import summary
        print(summary(a.base))
    elif a.command == 'snapshot':
        from package_ops import snapshot
        print(snapshot(a.message, push=not a.no_push) or 'Nothing to snapshot')
    elif a.command == 'sync-main':
        from package_ops import sync
        print(sync(a.base_branch))
        validate()
    elif a.command == 'render-md':
        from lab_ops import render_untouched
        for p in render_untouched(a.project):
            print(p)
    elif a.command == 'fix-sources':
        from lab_ops import fix_sources
        for p in a.paths:
            print(p, *fix_sources(p))
    elif a.command == 'task-keys':
        from task_keys import register
        print(json.dumps(register(project(a.project), a.prefix), indent=2))
    elif a.command == 'site':
        from research_site import generate
        validate()
        manifest = generate(ROOT, git('remote', 'get-url', 'origin'), git('rev-parse', 'HEAD'), dirty=bool(git('status', '--porcelain')))
        print(f'Generated website/research: {len(manifest["records"])} records, {len(manifest["projects"])} projects')
    elif a.command == 'init':
        init(a.project)
    elif a.command == 'new':
        print(new(a.project, a.kind).relative_to(ROOT))
    elif a.command == 'audit':
        audit(a.project, a.hypothesis)
    elif a.command in ('claim', 'release'):
        claim(a.project, a.task, a.run, getattr(a, 'expected', None))
    elif a.command == 'exec':
        return execute(a.project, a.run, a.argv)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
