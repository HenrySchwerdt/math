"""Generate VitePress Markdown from the provider-independent research ledger."""
import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote, urlsplit

from markdown_it import MarkdownIt

KINDS = {'TSK': 'Task', 'HYP': 'Hypothesis', 'RUN': 'Run', 'EXP': 'Experiment',
         'ALG': 'Algorithm', 'PRF': 'Proof attempt', 'REV': 'Review',
         'DEC': 'Decision', 'PAP': 'Paper'}
GUIDES = {'methodology': ('Research methodology', 'docs/METHODOLOGY.md'),
          'review': ('Evidence and independent review', 'docs/REVIEW.md'),
          'lean': ('Lean 4 and formal verification', 'docs/LEAN.md'),
          'handoff': ('Cross-provider handoff', 'docs/HANDOFF.md'),
          'claude': ('Start a research session', 'docs/CLAUDE_START.md'),
          'website': ('Updating this website', 'docs/WEBSITE.md')}


def text(value):
    """Render untrusted ledger values as Markdown text, never Vue or HTML."""
    value = html.escape(str(value), quote=False)
    for char in '\\`*_{}[]|#':
        value = value.replace(char, '\\' + char)
    return value.replace('\n', ' ')


def report(value):
    # The renderer disables input HTML and unsafe links, but preserves code exactly.
    # Its generated HTML sits inside the trusted v-pre wrapper, disabling Vue eval.
    return MarkdownIt("commonmark", {"html": False}).enable("table").render(value)


def repository_url(value):
    if value.startswith('git@github.com:'):
        value = 'https://github.com/' + value.split(':', 1)[1]
    value = value.removesuffix('.git').rstrip('/')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or parsed.hostname != 'github.com' or
            parsed.username or parsed.password or parsed.query or parsed.fragment or
            not re.fullmatch(r'/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', parsed.path)):
        raise ValueError('Website repository URL must be an HTTPS GitHub owner/repo URL')
    return value


def source_link(repo, commit, relative, label):
    return f'[{text(label)}]({repo}/blob/{quote(commit, safe="")}/{quote(str(relative), safe="/")})'


def reference_ids(d):
    run, review = d.get('run', {}), d.get('review', {})
    return set(d['refs'] + run.get('input_hypotheses', []) + run.get('reviews', [])
               + review.get('targets', []) + [v for v in
                 [run.get('task'), review.get('run'), d.get('task')] if v])


def timestamp(d):
    return d.get('run', {}).get('completed_at') or d['created_at']


def generate(root, repo, commit, dirty=False):
    root = Path(root).resolve()
    repo = repository_url(repo)
    if not re.fullmatch(r'[0-9a-f]{40,64}', commit):
        raise ValueError('Expected a full source commit hash')
    web = root / 'website'
    destination = web / 'research'
    if web.is_symlink() or destination.is_symlink():
        raise ValueError('Generated website paths must not be symlinks')
    if destination.exists():
        if not (destination / '.generated-by-research-cli').is_file():
            raise ValueError('Refusing to replace a directory not owned by the generator')
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    (destination / '.generated-by-research-cli').touch()
    rows, projects = [], []
    for base in sorted((root / 'research').iterdir()):
        if base.name.startswith('_') or not base.is_dir():
            continue
        if not re.fullmatch(r'[a-z][a-z0-9-]*', base.name) or base.is_symlink():
            raise ValueError('Invalid project directory')
        for path in sorted(base.glob('*/*.json')):
            if path.is_symlink():
                raise ValueError('Ledger records must not be symlinks')
            d = json.loads(path.read_text())
            if not re.fullmatch(r'(TSK|HYP|RUN|EXP|ALG|PRF|REV|DEC|PAP)-[0-9a-f-]{36}', d['id']):
                raise ValueError('Invalid artifact identifier')
            d = dict(d, project=base.name, source=str(path.relative_to(root)))
            rows.append(d)
        projects.append({'slug': base.name, 'title': 'ECDLP' if base.name == 'ecdlp' else base.name.replace('-', ' ').title()})
    rows.sort(key=lambda d: (timestamp(d), d['id']), reverse=True)
    by_id = {d['id']: d for d in rows}

    def page(relative, title, body):
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('---\ntitle: ' + json.dumps(title) + '\n---\n\n'
                        '<div v-pre>\n\n# ' + text(title) + '\n\n' + body +
                        '\n\n</div>\n')

    def link(d, prefix=''):
        return f'[{text(d["title"])}]({prefix}records/{d["id"]}.md)'

    def table(items, prefix=''):
        if not items:
            return '_No records yet._\n'
        lines = ['| Record | Project | Status | Outcome | Proof status |',
                 '| --- | --- | --- | --- | --- |']
        for d in items:
            lines.append(f'| {link(d, prefix)} | {text(d["project"])} | '
                         f'{text(d["status"])} | {text(d["outcome"] or "pending")} | '
                         f'{text(d["proof_status"])} |')
        return '\n'.join(lines) + '\n'

    for p in projects:
        base = root / 'research' / p['slug']
        own = [d for d in rows if d['project'] == p['slug']]
        p.update(records=len(own), open_tasks=sum(d['type'] == 'TSK' and d['status'] != 'completed' for d in own),
                 hypotheses=sum(d['type'] == 'HYP' for d in own),
                 formally_verified=sum(d['type'] in ('HYP', 'PRF') and d['proof_status'] == 'formally-verified' for d in own))
        body = ('## Current status\n\n' + report((base / 'STATUS.md').read_text()) +
                '\n\n## Backlog\n\n' + report((base / 'BACKLOG.md').read_text()) +
                '\n\n## Project records\n\n' + table(own, '../') +
                '\n' + source_link(repo, commit, base.relative_to(root) / 'STATUS.md', 'Source status in GitHub'))
        page(f'projects/{p["slug"]}.md', p['title'], body)

    for d in rows:
        body = (f'**{KINDS[d["type"]]}** · `{d["id"]}` · '
                f'[Project](../projects/{d["project"]}.md)\n\n'
                '| Task / artifact status | Reported outcome | Mathematical proof status |\n'
                '| --- | --- | --- |\n'
                f'| {text(d["status"])} | {text(d["outcome"] or "pending")} | {text(d["proof_status"])} |\n\n'
                '> Task completion and run outcomes are not proof certificates. '
                'Experimental evidence and independent review do not establish a theorem.\n\n')
        for heading, field in [('Research question', 'question'), ('Why this task', 'rationale'),
                               ('Next action', 'next_action'), ('Limitations and notes', 'notes')]:
            body += f'## {heading}\n\n{text(d[field])}\n\n'
        for heading, field in [('Success criteria', 'success_criteria'), ('Claims', 'claims'),
                               ('Assumptions', 'assumptions')]:
            if d.get(field):
                body += f'## {heading}\n\n' + '\n'.join('- ' + text(x) for x in d[field]) + '\n\n'
        if 'run' in d:
            r = d['run']
            body += '## Execution provenance\n\n'
            for label, key in [('Provider', 'provider'), ('Model', 'model'), ('Role', 'role'),
                               ('Started (UTC)', 'started_at'), ('Completed (UTC)', 'completed_at'),
                               ('Starting commit', 'starting_commit'), ('Result commit', 'resulting_commit')]:
                body += f'- **{label}:** {text(r[key] or "not recorded")}\n'
            if r['tests']:
                body += '\n### Recorded checks\n\n' + '\n'.join('- ' + text(x) for x in r['tests']) + '\n'
        related = [x for x in rows if x['id'] in reference_ids(d) or d['id'] in reference_ids(x)]
        body += '\n## Related tasks and results\n\n' + table(related, '../')
        evidence = sorted(set(d['evidence'] + d.get('run', {}).get('commands', [])))
        body += '\n## Sources and supporting evidence\n\n'
        body += '- ' + source_link(repo, commit, d['source'], 'Machine-readable metadata') + '\n'
        report_path = Path(d['source']).with_suffix('.md')
        body += '- ' + source_link(repo, commit, report_path, 'Original Markdown report') + '\n'
        for ev in evidence:
            if Path(ev).is_absolute() or '..' in Path(ev).parts:
                raise ValueError('Nonportable evidence path')
            body += '- ' + source_link(repo, commit, ev, Path(ev).name) + '\n'
        for source in d['sources']:
            url = urlsplit(source['url'])
            if url.scheme in ('http', 'https'):
                body += f'- [{text(source["title"])}]({quote(source["url"], safe="/:?=&%#@+;,-._~")}) — {text(source["locator"])}; retrieved {text(source["retrieved_at"])}\n'
        body += '\n## Research report\n\n' + report((root / report_path).read_text())
        page(f'records/{d["id"]}.md', d['title'], body)

    tasks = [d for d in rows if d['type'] == 'TSK']
    page('tasks.md', 'Research tasks',
         'Open work, active assignments and completed tasks, directly from the ledger.\n\n' +
         '\n\n'.join(f'## {title}\n\n' + table([d for d in tasks if d['status'] in statuses])
                       for title, statuses in [('Open', ['open']), ('In progress', ['active']),
                                               ('Blocked', ['blocked']), ('Completed', ['completed'])]))
    page('results.md', 'Results and evidence',
         'A result is presented with its recorded outcome and proof status. '
         'Infrastructure checks are not mathematical discoveries.\n\n'
         '## Formally verified research\n\n' +
         table([d for d in rows if d['type'] in ('HYP', 'PRF') and d['proof_status'] == 'formally-verified']) +
         '\n## Completed work\n\n' + table([d for d in rows if d['status'] == 'completed']) +
         '\n## Refuted claims\n\n' + table([d for d in rows if d['outcome'] == 'refuted']) +
         '\n## Blocked and unresolved work\n\n' + table([d for d in rows if d['status'] == 'blocked' or d['outcome'] in ('blocked', 'unresolved', 'inconclusive')]))
    page('activity.md', 'Research activity',
         'Chronology of recorded artifacts and run completions. Times are UTC; '
         'this is a Git snapshot, not a live agent monitor.\n\n' +
         '\n\n'.join(f'### {text(timestamp(d))}\n\n{link(d)}\n\n'
                       f'{text(KINDS[d["type"]])} · {text(d["project"])} · '
                       f'{text(d["status"])} / {text(d["outcome"] or "pending")}' for d in rows))
    page('records/index.md', 'All research records', table(rows, '../'))
    page('index.md', 'Follow the research',
         'This public notebook is generated from the same Git-versioned state used by '
         'Codex and Claude. Both primary research targets are open and unproved.\n\n'
         '## Projects\n\n' + '\n'.join(f'- [{p["title"]}](projects/{p["slug"]}.md)' for p in projects) +
         '\n\n## Explore\n\n- [Open tasks](tasks.md)\n- [Results and evidence](results.md)\n'
         '- [Activity timeline](activity.md)\n- [All records](records/index.md)\n\n'
         f'Source snapshot: [{commit[:7]}]({repo}/tree/{commit}).' + (' **Local preview includes uncommitted changes; source links refer to the last commit.**' if dirty else ''))
    for slug, (title, relative) in GUIDES.items():
        path = root / relative
        if path.is_file():
            page(f'guides/{slug}.md', title, report(path.read_text()) + '\n\n' +
                 source_link(repo, commit, relative, 'Canonical source document'))
    # Publish an allowlist, never command output, raw transcripts or private directories.
    public_records = [{k: d[k] for k in ('id', 'type', 'title', 'project', 'status',
                      'outcome', 'proof_status', 'question', 'next_action')} |
                      {'updated_at': timestamp(d)} for d in rows]
    manifest = dict(repository=repo, commit=commit, dirty=dirty, projects=projects, records=public_records)
    config_dir = web / '.vitepress'
    if config_dir.is_symlink():
        raise ValueError('Website config directory must not be a symlink')
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / 'ledger.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest
