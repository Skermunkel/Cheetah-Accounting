"""The person's private workspace: folders, profile, document index and logs. Never inside the app folder.

Layout (default ~/Cheetah/workspace, or $CHEETAH_WORKSPACE):
    profile.json                 who this is and which taxpayers (entities) we look after
    TASKS.md                     open work, most urgent first
    inbox/                       drop any document here; cheetah_ingest sorts it
    projects/<slug>/             files for the Claude Desktop Project of each entity
    <slug>/documents/<kind>/     originals, sorted by kind
    <slug>/extracted/            text extracted locally (cache, so documents are read once)
    <slug>/transactions/         parsed bank lines per account (TSV)
    <slug>/workpapers/           categorised periods and year summaries
    <slug>/out/                  PDFs and letters for the person to check, sign or submit
    <slug>/rules.json            how bank lines are categorised (grows as questions are answered)
    <slug>/decisions.jsonl       every judgement call, with the reason
    <slug>/documents.json        index of documents: hash, kind, date, key facts
"""
import datetime, hashlib, json, os, re, shutil
from pathlib import Path

APP = Path(__file__).resolve().parents[2]
KINDS = ['bank', 'certificates', 'invoices', 'receipts', 'sars', 'cipc', 'other']
ENTITY_KINDS = {'individual', 'sole-proprietor', 'company', 'close-corporation', 'trust'}


def root():
    p = Path(os.environ.get('CHEETAH_WORKSPACE') or Path.home() / 'Cheetah' / 'workspace').expanduser()
    p.mkdir(parents=True, exist_ok=True)
    (p / 'inbox').mkdir(exist_ok=True)
    return p


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:40] or 'me'


def profile():
    f = root() / 'profile.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {'entities': []}


def save_profile(p):
    (root() / 'profile.json').write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding='utf-8')


def entity(slug):
    e = next((e for e in profile()['entities'] if e['slug'] == slug), None)
    if not e:
        names = ', '.join(e['slug'] for e in profile()['entities']) or 'none yet (run cheetah-init)'
        raise ValueError(f'unknown entity {slug!r}; known: {names}')
    return e


def edir(slug):
    d = root() / slug
    for sub in ['documents', 'extracted', 'transactions', 'workpapers', 'out']:
        (d / sub).mkdir(parents=True, exist_ok=True)
    return d


def inside(base, rel):
    """Resolve rel under base and refuse anything that escapes it."""
    p = (base / rel).resolve()
    if not p.is_relative_to(base.resolve()):
        raise ValueError(f'{rel!r} is outside the workspace')
    return p


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_index(slug):
    f = edir(slug) / 'documents.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}


def save_index(slug, idx):
    (edir(slug) / 'documents.json').write_text(json.dumps(idx, indent=1, ensure_ascii=False), encoding='utf-8')


def log_decision(slug, question, decision, reason, source='the person', tax_year=None):
    row = {'date': datetime.date.today().isoformat(), 'entity': slug, 'tax_year': tax_year,
           'question': question, 'decision': decision, 'reason': reason, 'source': source}
    with open(edir(slug) / 'decisions.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return row


def unique(dest):
    n, stem = 1, dest.stem
    while dest.exists():
        n += 1
        dest = dest.with_name(f'{stem} ({n}){dest.suffix}')
    return dest


def file_into(src, slug, kind, date=None):
    """Move a document from the inbox to <slug>/documents/<kind>/, prefixed with its date when known."""
    d = edir(slug) / 'documents' / kind
    d.mkdir(parents=True, exist_ok=True)
    name = src.name if not date or src.name.startswith(date) else f'{date} {src.name}'
    dest = unique(d / name)
    shutil.move(str(src), dest)
    return dest
