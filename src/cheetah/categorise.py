"""Apply an entity's rules to its bank lines and write a working paper; group what is left as questions.

rules.json: {"rules": [{"match": "Engen|Shell", "treatment": "expense", "account": "Motor expenses",
                        "share": 0.25, "vat": "none", "note": "25% business use (person, 2026-11-16)"}]}
match is a case-insensitive regex on the description; optional "dates": [...] and "amount": -129.0 narrow a rule.
treatment: income, expense, personal, transfer, asset, loan, capital, tax, salary
share (expense/asset only): business part; the rest is personal (director loan for a company, drawings otherwise).
vat: standard (15% included), zero, exempt, none (no VAT, or no valid tax invoice). First matching rule wins.
"""
import csv, itertools, json, re
from collections import defaultdict
from pathlib import Path
from . import statements, workspace

TREATMENTS = {'income', 'expense', 'personal', 'transfer', 'asset', 'loan', 'capital', 'tax', 'salary'}
COLS = ['date', 'description', 'amount', 'treatment', 'account', 'share', 'business_amount', 'vat', 'note', 'source']


def load_rules(slug):
    f = workspace.edir(slug) / 'rules.json'
    return json.loads(f.read_text(encoding='utf-8'))['rules'] if f.exists() else []


def save_rules(slug, rules):
    (workspace.edir(slug) / 'rules.json').write_text(json.dumps({'rules': rules}, indent=1, ensure_ascii=False), encoding='utf-8')


def add_rule(slug, match, treatment, account, share=1.0, vat='none', note='', dates=None, amount=None):
    """Newest decision wins: one-off rules (dates/amount) go first, then general rules before older ones."""
    if treatment not in TREATMENTS:
        raise ValueError(f'treatment must be one of {sorted(TREATMENTS)}')
    re.compile(match)
    rule = {'match': match, 'treatment': treatment, 'account': account, 'share': share, 'vat': vat, 'note': note}
    if dates:
        rule['dates'] = dates
    if amount is not None:
        rule['amount'] = amount
    rules = [r for r in load_rules(slug) if not (r['match'] == match and r.get('dates') == dates and r.get('amount') == amount)]
    specific = lambda r: 'dates' in r or 'amount' in r
    rules.insert(0 if specific(rule) else sum(1 for _ in itertools.takewhile(specific, rules)), rule)
    save_rules(slug, rules)
    return rule


def merchant(desc):
    d = re.sub(r'^(Card: |POS Purchase |Card Purchase |Fuel Purchase |Debit Order |Magtape (Debit|Credit) |'
               r'(FNB App |Internet |Immediate )?(Geo )?Payment To |Payment From |Yoco ?\*|Ik \*|Pp \*|Paypal \*)', '', desc, flags=re.I)
    d = re.sub(r'\s+\d[\d*]{5,}.*$|\s+\d{2} [A-Za-z]{3}$|\s+\d{2}/\d{2}$', '', d)
    return (d.strip() or desc).title()[:40]


def match(rules, r):
    for x in rules:
        if re.search(x['match'], r['description'], re.I) and r['date'] in x.get('dates', [r['date']]) \
                and ('amount' not in x or abs(float(r['amount']) - x['amount']) < 0.005):
            return x
    return None


def run(slug, start, end, label):
    """Categorise every account of the entity for start..end into workpapers/<label>.tsv."""
    rules, out = load_rules(slug), []
    for f in sorted((workspace.edir(slug) / 'transactions').glob('*.tsv')):
        for r in statements.load(f, start, end):
            x = match(rules, r)
            amt = float(r['amount'])
            t, a, share = (x['treatment'], x['account'], float(x.get('share', 1.0))) if x else ('ASK', '', 0.0)
            biz = round(amt * share, 2) if t in ('expense', 'asset') else (amt if t == 'income' else 0.0)
            out.append({'date': r['date'], 'description': r['description'], 'amount': amt, 'treatment': t, 'account': a,
                        'share': share, 'business_amount': biz, 'vat': x.get('vat', 'none') if x else '',
                        'note': x.get('note', '') if x else '', 'source': f.stem})
    out.sort(key=lambda r: r['date'])
    path = workspace.edir(slug) / 'workpapers' / f'{label}.tsv'
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, COLS, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(out)
    return path, summarise(out, workspace.entity(slug).get('vat_registered'))


def summarise(rows, vat_registered=False, top=25):
    by_t, by_acc, ask = defaultdict(float), defaultdict(float), defaultdict(lambda: [0, 0.0, ''])
    for r in rows:
        by_t[r['treatment']] += r['amount']
        if r['treatment'] in ('income', 'expense'):
            by_acc[r['account']] += r['business_amount']
        if r['treatment'] == 'ASK':
            m = ask[merchant(r['description'])]
            m[0] += 1
            m[1] += r['amount']
            m[2] = m[2] or r['date']
    s = {'lines': len(rows), 'by_treatment': {k: round(v, 2) for k, v in sorted(by_t.items())},
         'by_account': {k: round(v, 2) for k, v in sorted(by_acc.items(), key=lambda x: x[1])},
         'unanswered_lines': sum(v[0] for v in ask.values()),
         'questions': [{'merchant': k, 'count': n, 'total': round(t, 2), 'first_date': d}
                       for k, (n, t, d) in sorted(ask.items(), key=lambda x: x[1][1])[:top]]}
    if len(ask) > top:
        s['more_questions'] = len(ask) - top
    if vat_registered:
        out_vat = sum(r['amount'] * 15 / 115 for r in rows if r['treatment'] == 'income' and r['vat'] == 'standard')
        in_vat = sum(-r['business_amount'] * 15 / 115 for r in rows if r['treatment'] in ('expense', 'asset') and r['vat'] == 'standard')
        s['vat'] = {'output_vat': round(out_vat, 2), 'input_vat_if_tax_invoices_held': round(in_vat, 2),
                    'zero_rated_sales': round(sum(r['amount'] for r in rows if r['treatment'] == 'income' and r['vat'] == 'zero'), 2),
                    'note': 'claim input VAT only for lines with a valid tax invoice in the company name'}
    return s


def read(path):
    rows = list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))
    for r in rows:
        for k in ('amount', 'share', 'business_amount'):
            r[k] = float(r[k] or 0)
    return rows


def lines(slug, label, merchant_text=None, treatment=None, limit=40):
    """A few working-paper lines, for answering one question without loading the whole year."""
    rows = read(workspace.edir(slug) / 'workpapers' / f'{label}.tsv')
    rows = [r for r in rows if (not treatment or r['treatment'] == treatment)
            and (not merchant_text or re.search(merchant_text, r['description'], re.I))]
    return [f"{r['date']} | {r['description'][:60]} | {r['amount']:.2f} | {r['treatment']} {r['account']}" for r in rows[:limit]], len(rows)


def path_of(slug, label):
    p = workspace.edir(slug) / 'workpapers' / f'{label}.tsv'
    if not p.exists():
        raise ValueError(f'no working paper {label!r}; run cheetah_categorise first')
    return Path(p)
