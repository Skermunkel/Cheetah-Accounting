"""Cheetah MCP server for Claude Desktop: local tools over the person's workspace.

Heavy work (reading documents, parsing statements, totals) happens here on the PC; tools return short summaries
so the Free plan's usage goes on questions and decisions, not on raw text.
"""
import datetime, json, os, platform, re, subprocess
from pathlib import Path
from mcp.server.mcpserver import MCPServer
from . import books, categorise, extract, reports, statements, tax, upkeep, workspace as ws

mcp = MCPServer('cheetah', instructions=(
    'Cheetah Accounting: South African personal and small-business tax helper. At the start of a chat call '
    'cheetah_status, then cheetah_guide("ground-rules") if it is not already in the Project. Prepare and explain; '
    'never submit returns or make payments; ask the person when unsure.'))
GUIDES = ws.APP / 'knowledge'


def j(x):
    return json.dumps(x, ensure_ascii=False, indent=1, default=str)


def tasks_file():
    f = ws.root() / 'TASKS.md'
    if not f.exists():
        f.write_text('# Tasks (most urgent first)\n\n', encoding='utf-8')
    return f


@mcp.tool()
def cheetah_status(entity: str = '') -> str:
    """Workspace overview: entities, documents, statements, working papers, inbox, open tasks, recent decisions."""
    p = ws.profile()
    if not p['entities']:
        return j({'workspace': str(ws.root()), 'version': upkeep.local_version(),
                  'state': 'not set up yet: follow cheetah_guide("init")'})
    out = {'workspace': str(ws.root()), 'version': upkeep.local_version(), 'person': p.get('person'), 'entities': []}
    for e in p['entities']:
        if entity and e['slug'] != entity:
            continue
        d = ws.edir(e['slug'])
        idx = ws.load_index(e['slug'])
        kinds = {}
        for v in idx.values():
            kinds[v['kind']] = kinds.get(v['kind'], 0) + 1
        accts = {}
        for f in sorted((d / 'transactions').glob('*.tsv')):
            rows = statements.load(f)
            if rows:
                accts[f.stem] = f"{len(rows)} lines {rows[0]['date']}..{rows[-1]['date']}"
        dec = (d / 'decisions.jsonl').read_text(encoding='utf-8').splitlines()[-5:] if (d / 'decisions.jsonl').exists() else []
        inbox = [x for x in (ws.root() / 'inbox' / e['slug']).glob('*') if x.is_file()] if (ws.root() / 'inbox' / e['slug']).exists() else []
        out['entities'].append({**{k: e.get(k) for k in ('slug', 'name', 'kind', 'vat_registered', 'paye_registered', 'year_end', 'bookkeeping')},
                                'documents': kinds, 'accounts': accts,
                                'workpapers': sorted(x.stem for x in (d / 'workpapers').glob('*.tsv')),
                                'inbox_waiting': len(inbox), 'recent_decisions': [json.loads(x)['decision'] for x in dec]})
    loose = [x.name for x in (ws.root() / 'inbox').glob('*') if x.is_file()]
    if loose:
        out['inbox_unsorted'] = loose[:20]
    out['open_tasks'] = [l[6:] for l in tasks_file().read_text(encoding='utf-8').splitlines() if l.startswith('- [ ] ')][:12]
    return j(out)


@mcp.tool()
def cheetah_guide(topic: str = 'index') -> str:
    """Instructions and SA tax reference, read on demand. topic: index, init, ground-rules, documents, bookkeeping,
    zoho-books, personal-tax, company-tax, vat-paye, catch-up, records."""
    f = GUIDES / f'{re.sub(r"[^a-z0-9-]", "", topic.lower())}.md'
    if not f.exists():
        return 'topics: ' + ', '.join(sorted(x.stem for x in GUIDES.glob('*.md')))
    return f.read_text(encoding='utf-8')


@mcp.tool()
def cheetah_setup(person_name: str, entities: list[dict]) -> str:
    """Create or update the workspace. Each entity: {"name", "kind": individual|sole-proprietor|company|close-corporation|trust,
    "year_end": "02" (month the financial year ends), "vat_registered": bool, "paye_registered": bool,
    "banks": ["FNB cheque", ...], "bookkeeping": "zoho"|"none", "registration_number": optional, "notes": optional}.
    Tax numbers are optional; they are only stored on this PC."""
    p = ws.profile()
    p['person'] = person_name
    p.setdefault('created', datetime.date.today().isoformat())
    made = []
    for e in entities:
        if e.get('kind') not in ws.ENTITY_KINDS:
            raise ValueError(f"kind must be one of {sorted(ws.ENTITY_KINDS)}")
        e['slug'] = e.get('slug') or ws.slugify(e['name'])
        e.setdefault('year_end', '02')
        p['entities'] = [x for x in p['entities'] if x['slug'] != e['slug']] + [e]
        ws.save_profile(p)
        d = ws.edir(e['slug'])
        (ws.root() / 'inbox' / e['slug']).mkdir(parents=True, exist_ok=True)
        if not (d / 'rules.json').exists() and e['kind'] != 'individual':
            starter = ws.APP / 'templates' / 'rules-starter.json'
            (d / 'rules.json').write_text(starter.read_text(encoding='utf-8'), encoding='utf-8')
        made.append(e['slug'])
        project_files(e)
    tasks_file()
    return j({'workspace': str(ws.root()), 'entities': made,
              'next': 'help the person create one Claude Project per entity from projects/<slug>/ (see init guide)'})


def project_files(e):
    tpl = (ws.APP / 'templates' / 'project-instructions.md').read_text(encoding='utf-8')
    d = ws.root() / 'projects' / e['slug']
    d.mkdir(parents=True, exist_ok=True)
    kinds = {'individual': 'personal income tax (ITR12)', 'sole-proprietor': 'personal income tax with business income (ITR12)',
             'company': 'company tax (ITR14), financial statements and CIPC', 'close-corporation': 'CC tax (ITR14), financial statements and CIPC',
             'trust': 'trust tax (ITR12T)'}
    fill = {'NAME': e['name'], 'SLUG': e['slug'], 'WHAT': kinds[e['kind']], 'WORKSPACE': str(ws.root()),
            'GUIDE': 'personal-tax' if e['kind'] in ('individual', 'sole-proprietor') else 'company-tax'}
    for k, v in fill.items():
        tpl = tpl.replace('{{' + k + '}}', v)
    (d / 'INSTRUCTIONS.md').write_text(tpl, encoding='utf-8')
    about = [f"# {e['name']}", '', f"- Workspace folder: {ws.root() / e['slug']}", f"- Kind: {e['kind']} ({kinds[e['kind']]})",
             f"- Financial year ends: month {e['year_end']}"]
    for k in ('registration_number', 'vat_registered', 'paye_registered', 'banks', 'bookkeeping', 'notes'):
        if e.get(k) not in (None, '', []):
            about.append(f'- {k.replace("_", " ").capitalize()}: {e[k]}')
    about += ['', 'Live details (documents, statements, tasks, decisions) come from the cheetah_status tool, not from this file.']
    (d / 'ABOUT.md').write_text('\n'.join(about) + '\n', encoding='utf-8')
    (d / 'GROUND-RULES.md').write_text((GUIDES / 'ground-rules.md').read_text(encoding='utf-8'), encoding='utf-8')


@mcp.tool()
def cheetah_ingest(entity: str = '') -> str:
    """Read, sort and index every document in the inbox (inbox/<entity>/, or the loose inbox when entity is given).
    Bank statements are parsed into transactions and checked against their opening and closing balances."""
    jobs = []
    for e in ws.profile()['entities']:
        if not entity or e['slug'] == entity:
            box = ws.root() / 'inbox' / e['slug']
            jobs += [(e['slug'], x) for x in sorted(box.glob('*')) if x.is_file()] if box.exists() else []
    if entity:
        ws.entity(entity)
        jobs += [(entity, x) for x in sorted((ws.root() / 'inbox').glob('*')) if x.is_file()]
    done = []
    for slug, f in jobs:
        if f.suffix.lower() not in extract.SUPPORTED:
            done.append({'file': f.name, 'skipped': f'unsupported type {f.suffix}'})
            continue
        idx = ws.load_index(slug)
        h = ws.sha256(f)
        if h in idx:
            dup = ws.unique(ws.edir(slug) / 'documents' / 'duplicates' / f.name)
            dup.parent.mkdir(exist_ok=True)
            f.rename(dup)
            done.append({'file': f.name, 'duplicate_of': idx[h]['path']})
            continue
        try:
            text, method = extract.extract(f)
        except Exception as ex:  # one unreadable file must not stop the rest
            done.append({'file': f.name, 'error': str(ex)[:200]})
            continue
        kind, label = extract.kind_of(text, f.name)
        facts = extract.facts(text, kind)
        first = facts.get('dates', '')[:10] or None
        dest = ws.file_into(f, slug, kind, first)
        doc_id = h[:10]
        (ws.edir(slug) / 'extracted' / f'{doc_id}.txt').write_text(text, encoding='utf-8')
        rec = {'id': doc_id, 'path': str(dest.relative_to(ws.root())), 'kind': kind, 'what': label, 'method': method,
               'facts': facts, 'added': datetime.date.today().isoformat()}
        if kind == 'bank':
            rec['statement'] = import_statement(slug, doc_id, text, dest.name, facts)
        idx[h] = rec
        ws.save_index(slug, idx)
        done.append({k: rec[k] for k in ('id', 'path', 'what', 'facts') if k in rec} | ({'statement': rec['statement']} if 'statement' in rec else {}))
    return j({'processed': len(done), 'documents': done} if done else 'inbox is empty: ask the person to drop documents in ' + str(ws.root() / 'inbox'))


def import_statement(slug, doc_id, text, name, facts, account=None):
    try:
        rows, chk = statements.parse(text, name)
    except ValueError as ex:
        return {'error': str(ex)}
    if not rows:
        return {'error': 'no transaction lines recognised; read the document and ask the maintainer for a parser (cheetah_feedback)'}
    account = account or ws.slugify(f"{facts.get('bank', 'bank')} {facts.get('account_last4', '')}")
    overlap = statements.store(ws.edir(slug) / 'transactions' / f'{account}.tsv', rows, doc_id)
    chk['account'] = account
    if overlap:
        chk['overlaps_with'] = overlap
    return chk


def find_doc(slug, doc):
    for h, v in ws.load_index(slug).items():
        if doc in (v['id'], h) or doc.lower() in v['path'].lower():
            return v
    raise ValueError(f'no document matching {doc!r}')


@mcp.tool()
def cheetah_read(entity: str, doc: str, search: str = '', start: int = 0, max_chars: int = 3000) -> str:
    """Read a document's extracted text. With search (regex), return only matching lines; otherwise a slice from start."""
    v = find_doc(entity, doc)
    text = (ws.edir(entity) / 'extracted' / f"{v['id']}.txt").read_text(encoding='utf-8')
    if search:
        hits = [l.strip() for l in text.splitlines() if re.search(search, l, re.I)]
        return '\n'.join(hits)[:max_chars] or 'no matching lines'
    part = text[start:start + max_chars]
    more = len(text) - start - len(part)
    return part + (f'\n[... {more} more characters; call again with start={start + len(part)}]' if more > 0 else '')


@mcp.tool()
def cheetah_import_statement(entity: str, doc: str, account: str) -> str:
    """Parse (again) one bank or card statement into the named account, e.g. "fnb-cheque" or "capitec-savings"."""
    v = find_doc(entity, doc)
    text = (ws.edir(entity) / 'extracted' / f"{v['id']}.txt").read_text(encoding='utf-8')
    return j(import_statement(entity, v['id'], text, v['path'], v.get('facts', {}), ws.slugify(account)))


@mcp.tool()
def cheetah_categorise(entity: str, start: str, end: str, label: str) -> str:
    """Apply the entity's rules to all its bank lines from start to end (YYYY-MM-DD) into working paper <label>
    (e.g. "FY2025"). Returns totals and the unanswered merchants to ask the person about."""
    path, summary = categorise.run(entity, start, end, label)
    return j({'workpaper': str(path.relative_to(ws.root())), **summary})


@mcp.tool()
def cheetah_rule(entity: str, match: str, treatment: str, account: str, why: str, share: float = 1.0, vat: str = 'none',
                 dates: list[str] | None = None, amount: float | None = None) -> str:
    """Record how lines matching `match` (regex on the description) are treated, and why. treatment: income, expense,
    personal, transfer, asset, loan, capital, tax, salary. share: business part of an expense (0..1).
    vat: standard|zero|exempt|none. Re-run cheetah_categorise afterwards."""
    rule = categorise.add_rule(entity, match, treatment, account, share, vat, why, dates, amount)
    ws.log_decision(entity, f'how to treat {match}', f'{treatment} {account} {share:.0%}', why)
    return j(rule)


@mcp.tool()
def cheetah_lines(entity: str, label: str, search: str = '', treatment: str = '', limit: int = 40) -> str:
    """Show working-paper lines matching a description regex and/or treatment (e.g. "ASK"), for one question at a time."""
    rows, n = categorise.lines(entity, label, search or None, treatment or None, limit)
    return '\n'.join(rows) + (f'\n[{n - len(rows)} more]' if n > len(rows) else '')


@mcp.tool()
def cheetah_year_summary(entity: str, label: str) -> str:
    """Draft income statement, balance-sheet movements and owner/director account for a categorised year."""
    return books.year(entity, label)[0]


@mcp.tool()
def cheetah_review_pdf(entity: str, label: str, treatment: str = 'personal') -> str:
    """PDF of all personal (or other treatment) and unanswered lines, for the person to mark business items on paper."""
    out, n = reports.review_pdf(entity, label, treatment)
    return f'{n} lines -> {out}'


@mcp.tool()
def cheetah_tax_estimate(tax_year: int, age: int, employment_income: float = 0, interest: float = 0, other_income: float = 0,
                         ra_contributions: float = 0, medical_contributions: float = 0, medical_out_of_pocket: float = 0,
                         medical_members: int = 0, medical_months: int = 12, paye_paid: float = 0, provisional_paid: float = 0,
                         disability: bool = False) -> str:
    """Estimate an individual's income tax for a tax year (2025 = Mar 2024-Feb 2025) to check SARS's assessment.
    employment_income: taxable total from IRP5s; other_income: net business or rental profit; medical_members: people on the scheme."""
    return j(tax.individual(tax_year, age, employment_income, interest, other_income, ra_contributions, medical_contributions,
                            medical_out_of_pocket, medical_members, medical_months, paye_paid, provisional_paid, disability))


@mcp.tool()
def cheetah_company_tax(year_end: str, taxable_income: float) -> str:
    """Company income tax at the standard rate for a financial year ending year_end (YYYY-MM-DD)."""
    return j(tax.company(year_end, taxable_income))


@mcp.tool()
def cheetah_save_letter(entity: str, filename: str, title: str, body: str) -> str:
    """Save a letter, note or motivation as PDF + editable text in <entity>/out/. Leave date and signature lines blank."""
    return str(reports.letter_pdf(entity, filename, title, body))


@mcp.tool()
def cheetah_zoho_export(entity: str, label: str, account: str = '') -> str:
    """CSV of a working paper's bank lines for Zoho Books Banking > Import Statement (one upload, no API calls)."""
    out, n = reports.zoho_bank_csv(entity, label, account or None)
    return f'{n} lines -> {out}'


@mcp.tool()
def cheetah_note(entity: str, kind: str, text: str, reason: str = '') -> str:
    """kind "decision": log a judgement call with its reason. kind "task": add an open task. kind "done": tick off the
    open task containing text."""
    if kind == 'decision':
        return j(ws.log_decision(entity, text, text, reason))
    f = tasks_file()
    lines = f.read_text(encoding='utf-8').splitlines()
    if kind == 'task':
        lines.append(f'- [ ] ({entity}) {text}')
    elif kind == 'done':
        i = next((i for i, l in enumerate(lines) if l.startswith('- [ ] ') and text.lower() in l.lower()), None)
        if i is None:
            return 'no open task contains that text'
        lines[i] = lines[i].replace('- [ ] ', f'- [x] {datetime.date.today().isoformat()} ', 1)
    else:
        return 'kind must be decision, task or done'
    f.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 'saved'


@mcp.tool()
def cheetah_open_folder(entity: str = '', sub: str = '') -> str:
    """Open a workspace folder in the file manager (e.g. the inbox, or an entity's out/ folder) for the person."""
    p = ws.inside(ws.root(), str(Path(entity) / sub) if entity else (sub or '.'))
    p.mkdir(parents=True, exist_ok=True)
    if platform.system() == 'Windows':
        os.startfile(p)  # noqa: only on Windows
    else:
        subprocess.Popen(['open' if platform.system() == 'Darwin' else 'xdg-open', str(p)])
    return f'opened {p}'


@mcp.tool()
def cheetah_update(check_only: bool = False) -> str:
    """Check for or install the latest Cheetah version from GitHub. Workspace data is never touched or sent."""
    return upkeep.update(check_only)


@mcp.tool()
def cheetah_feedback(title: str, body: str) -> str:
    """Open a pre-filled GitHub issue for the maintainer: a bug, a bank format that failed, an idea. Write it without
    personal details (names, numbers, amounts); they are also masked automatically. The person submits it themselves."""
    t, b, url = upkeep.feedback(title, body)
    return f'opened in the browser for the person to check and submit.\nTitle: {t}\n{b}'


def guide_prompt(path):
    def prompt() -> str:
        return path.read_text(encoding='utf-8')
    return prompt


for _g in sorted(GUIDES.glob('*.md')):  # the same guides as prompts: "+ > Add from cheetah" in Claude Desktop
    mcp.prompt(name=f'cheetah-{_g.stem}', description=f'Cheetah guide: {_g.stem}')(guide_prompt(_g))


def main():
    mcp.run()


if __name__ == '__main__':
    main()
