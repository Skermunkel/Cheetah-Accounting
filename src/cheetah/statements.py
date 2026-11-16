"""Turn bank and card statements (PDF text, OCR text or CSV exports) into transaction rows, and prove they are complete.

Rows: date (ISO), description, amount (money in positive, out negative), balance ('' when the statement has none).
The check that makes this dependable for any bank: opening balance + sum of amounts must equal the closing balance,
and where a running balance is printed, each line's sign comes from the change in balance, not from guessing.
"""
import csv, datetime, re
from .extract import MONTHS, csv_rows, dates

AMT = r'-?\(?\d{1,3}(?:[ ,]\d{3})*\.\d{2}\)?(?:\s?(?:Cr|Dr|CR|DR))?-?'
TOKEN = re.compile(r'(?<![\d.])' + AMT + r'(?![\d])')
LEAD = re.compile(r'^\s*(\d{4}[-/]\d{2}[-/]\d{2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2} [A-Za-z]{3}(?: \d{4})?)\s+(.*)$')


def num(tok, plain_is_debit=False):
    """Amount token to a signed number. plain_is_debit: the statement marks credits "Cr" and leaves debits bare (FNB)."""
    t = tok.replace(' ', '').replace(',', '')
    debit = re.search(r'Dr|DR', t) or t.startswith('-') or t.endswith('-') or t.startswith('(')
    sign = -1 if debit or (plain_is_debit and not re.search(r'Cr|CR', t)) else 1
    return sign * float(re.sub(r'[^\d.]', '', t))


def period(text):
    """(start, end) dates of the statement, from its header."""
    m = re.search(r'(?:statement period|period)\s*:?\s*(.+?)\s+(?:to|-)\s+(.+?)(?:\s{2,}|$)', text[:20000], re.I | re.M)
    if m:
        a, b = dates(m.group(1)), dates(m.group(2))
        if a and b:
            return a[0], b[0]
    ds = sorted(dates(text[:20000]))
    return (ds[0], ds[-1]) if ds else (None, None)


def iso(s, start=None, end=None):
    s = s.strip()
    for f in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y', '%d %b %Y', '%d %B %Y', '%Y%m%d']:
        try:
            return datetime.datetime.strptime(s, f).date().isoformat()
        except ValueError:
            pass
    m = re.fullmatch(r'(\d{1,2}) ([A-Za-z]{3})', s)  # "05 Mar": take the year from the statement period
    if m and start and end:
        mo = MONTHS[m.group(2).lower()]
        y = int(start[:4]) if start[:4] != end[:4] and mo >= int(start[5:7]) else int(end[:4])
        return datetime.date(y, mo, int(m.group(1))).isoformat()
    return None


def balance_after(label, text, plain_is_debit=False):
    m = re.search('(?:' + label + r')[^\n\d-]{0,40}(' + AMT + ')', text, re.I)
    return num(m.group(1), plain_is_debit) if m else None


def parse_text(text):
    """Any bank's statement text: lines that start with a date and end in amounts (amount, balance, maybe a fee column).
    Where a running balance is printed, the reading of the amounts that continues the balance wins."""
    plain_debit = bool(re.search(r'\d\.\d{2} ?(Cr|CR)\b', text))   # Cr-suffix style: bare amounts are debits
    n = lambda tok: num(tok, plain_debit)
    start, end = period(text)
    opening = balance_after(r'opening balance|balance brought forward|balance b/f|previous balance', text, plain_debit)
    closing = balance_after(r'closing balance|balance carried forward|balance c/f', text, plain_debit)
    rows, prev = [], opening
    for line in text.splitlines():
        m = LEAD.match(line)
        if not m:
            continue
        d = iso(m.group(1), start, end)
        toks = list(TOKEN.finditer(m.group(2)))
        if not d or not toks or re.match(r'(opening|closing) balance|balance (brought|carried)', m.group(2).strip(), re.I):
            continue
        # candidates (amount token, balance token): last two, or the two before a trailing fee/charges column
        cands = [(len(toks) - 2, len(toks) - 1)] + ([(len(toks) - 3, len(toks) - 2)] if len(toks) >= 3 else []) \
            if len(toks) >= 2 else [(0, None)]
        if len(toks) == 1 and prev is not None and abs(n(toks[0].group()) - prev) < 0.005:
            continue                                                  # balance-only line, e.g. "Rate Change 20 000.00Dr"
        pick, amt, bal = cands[0], None, None
        for a, b in cands:
            va, vb = n(toks[a].group()), (n(toks[b].group()) if b is not None else None)
            if vb is not None and prev is not None and abs(abs(round(vb - prev, 2)) - abs(va)) < 0.005:
                pick, amt, bal = (a, b), round(vb - prev, 2), vb      # the running balance decides the sign
                break
        if amt is None:
            a, b = pick
            amt, bal = n(toks[a].group()), (n(toks[b].group()) if b is not None else None)
            if bal is None and not plain_debit and amt > 0 and not re.search(r'Cr|CR', toks[a].group()):
                amt = -amt                                            # no balance column: bare amounts are debits
        desc = re.sub(r'\s{2,}', ' ', m.group(2)[:toks[pick[0]].start()]).strip()
        rows.append({'date': d, 'description': desc, 'amount': round(amt, 2), 'balance': '' if bal is None else bal})
        prev = bal if bal is not None else prev
    return rows, check(rows, opening, closing, start, end)


HEAD = {'date': r'date', 'description': r'desc|narr|detail|particular|reference|transaction$',
        'amount': r'^amount|^value', 'debit': r'debit|money out|withdraw|paid out', 'credit': r'credit|money in|deposit|paid in',
        'balance': r'balance'}


def parse_csv(text):
    """Bank CSV exports (FNB, Capitec, Absa, Standard Bank, Nedbank...): find the header row, map columns by name."""
    rows = csv_rows(text)
    for i, r in enumerate(rows):
        low = [c.strip().lower() for c in r]
        if any(re.search('date', c) for c in low) and any(re.search('amount|debit|credit|money', c) for c in low):
            col = {}
            for key, pat in HEAD.items():
                j = next((j for j, c in enumerate(low) if re.search(pat, c) and j not in col.values()), None)
                if j is not None:
                    col[key] = j
            break
    else:
        raise ValueError('no header row with a date and an amount column; export the statement as CSV with headers')
    out = []
    for r in rows[i + 1:]:
        if len(r) <= col['date'] or not r[col['date']].strip():
            continue
        d = iso(r[col['date']])
        if not d:
            continue
        val = lambda k: num(r[col[k]]) if k in col and len(r) > col[k] and re.search(r'\d', r[col[k]]) else 0.0
        amt = val('amount') if 'amount' in col else abs(val('credit')) - abs(val('debit'))
        bal = val('balance') if 'balance' in col and len(r) > col['balance'] and re.search(r'\d', r[col['balance']]) else ''
        desc = ' '.join(r[col['description']].split()) if 'description' in col else ''
        out.append({'date': d, 'description': desc, 'amount': round(amt, 2), 'balance': bal})
    # some exports list newest first: put in date order, keeping same-day order consistent with the balances
    if len(out) > 1 and out[0]['date'] > out[-1]['date']:
        out.reverse()
    opening = out[0]['balance'] - out[0]['amount'] if out and out[0]['balance'] != '' else None
    closing = out[-1]['balance'] if out and out[-1]['balance'] != '' else None
    return out, check(out, opening, closing, out[0]['date'] if out else None, out[-1]['date'] if out else None)


def check(rows, opening, closing, start, end):
    total = round(sum(r['amount'] for r in rows), 2)
    c = {'period': f'{start} .. {end}', 'lines': len(rows), 'money_in': round(sum(r['amount'] for r in rows if r['amount'] > 0), 2),
         'money_out': round(sum(r['amount'] for r in rows if r['amount'] < 0), 2), 'opening': opening, 'closing': closing}
    if opening is not None and closing is not None:
        diff = round(opening + total - closing, 2)
        c['reconciles'] = abs(diff) < 0.01
        if not c['reconciles']:
            c['difference'] = diff
            breaks = []  # lines where the running balance does not follow: the place to look
            prev = opening
            for r in rows:
                if r['balance'] != '':
                    if abs(prev + r['amount'] - r['balance']) > 0.005:
                        breaks.append(f"{r['date']} {r['description'][:40]} {r['amount']}")
                    prev = r['balance']
                else:
                    prev += r['amount']
            c['check_lines'] = breaks[:10]
    else:
        c['reconciles'] = None
        c['note'] = 'no opening/closing balance found: compare the totals with the statement yourself'
    return c


def parse(text, name):
    if name.lower().endswith(('.csv', '.tsv')):
        return parse_csv(text)
    return parse_text(text)


FIELDS = ['date', 'description', 'amount', 'balance', 'source']


def store(path, rows, source):
    """Add one statement's rows to an account file. Re-importing the same document replaces its rows."""
    old = list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t')) if path.exists() else []
    keep = [r for r in old if r['source'] != source]
    overlap = sorted({r['source'] for r in keep if rows and rows[0]['date'] <= r['date'] <= rows[-1]['date']})
    new = keep + [dict(r, source=source) for r in rows]
    new.sort(key=lambda r: r['date'])  # stable: same-day lines keep statement order
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, FIELDS, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(new)
    return overlap


def load(path, start=None, end=None):
    if not path.exists():
        return []
    rows = list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))
    return [r for r in rows if (not start or r['date'] >= start) and (not end or r['date'] <= end)]
