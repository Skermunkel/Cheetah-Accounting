"""Draft one financial year from a categorised working paper: income statement, balance-sheet movements, owner account.

workpapers/<label>.json (optional) adds what is not on the bank statements:
  {"owner_opening": -73740.0,           # director loan / owner account at the start; negative = business owes the owner
   "depreciation": {"Laptop": 4200.0},  # wear-and-tear for the year, per asset
   "journals": [{"lines": {"Interest paid": -2567.72, "Loan - bank": 2567.72}, "why": "loan interest per loan statement"}],
                                        # accounts starting Loan, Equipment, Asset, Capital, VAT, Accounts, Owner or
                                        # Director are balance-sheet accounts; the rest are income or expenses
   "salary_total": 95750.0}             # company only: director salary for the year (needs PAYE registration)
Signs follow the bank: money out is negative. A working draft for checking, not signed financial statements.
"""
import json, re
from collections import defaultdict
from . import categorise, workspace

BALANCE = ('asset', 'loan', 'capital')


def year(slug, label):
    e = workspace.entity(slug)
    company = e['kind'] in ('company', 'close-corporation', 'trust')
    owner = 'Director loan' if company else "Owner's drawings"
    rows = categorise.read(categorise.path_of(slug, label))
    extra_f = workspace.edir(slug) / 'workpapers' / f'{label}.json'
    o = json.loads(extra_f.read_text(encoding='utf-8')) if extra_f.exists() else {}
    acc, bs, own = defaultdict(float), defaultdict(float), defaultdict(float)
    ask = [r for r in rows if r['treatment'] == 'ASK']
    for r in rows:
        t, a, amt = r['treatment'], r['account'], r['amount']
        if t in ('income', 'expense'):
            acc[(t, a)] += r['business_amount']
            if t == 'expense' and r['share'] < 1:
                own[f'private share of {a.lower()}'] += amt - r['business_amount']
        elif t == 'asset':
            bs[a] += r['business_amount']
            if r['share'] < 1:
                own[f'private share of {a.lower()}'] += amt - r['business_amount']
        elif t in ('loan', 'capital'):
            bs[a] += amt
        elif t == 'personal':
            own['private spending and owner deposits'] += amt
        elif t == 'salary':
            acc[('expense', 'Salaries - director' if company else 'Drawings')] += amt
        elif t == 'tax':
            bs['SARS payments (income tax, VAT, PAYE)'] += amt
    for j in o.get('journals', []):
        if abs(sum(j['lines'].values())) >= 0.005:
            raise ValueError(f"journal does not balance: {j['why']}")
        for k, v in j['lines'].items():
            if k in bs or re.match(r'(Loan|Equipment|Asset|Capital|VAT|Accounts|Owner|Director)', k):
                bs[k] += v
            elif ('expense', k) in acc or ('income', k) not in acc and v < 0:
                acc[('expense', k)] += v
            else:
                acc[('income', k)] += v
    if company and 'salary_total' in o:
        paid = -acc[('expense', 'Salaries - director')]
        in_kind = o['salary_total'] - paid  # private spending declared as salary, up to the agreed total
        acc[('expense', 'Salaries - director')] -= in_kind
        own['private spending declared as salary'] += in_kind
    w = []
    w.append(f"# {e['name']}: {label} draft\n")
    w.append('## Income statement')
    inc = sum(v for (t, _), v in acc.items() if t == 'income')
    for (t, a), v in sorted(acc.items(), key=lambda x: (x[0][0] != 'income', x[1])):
        w.append(f'  {a:50} {v:12,.2f}')
    dep = sum(o.get('depreciation', {}).values())
    for k, v in o.get('depreciation', {}).items():
        w.append(f"  {'Depreciation - ' + k:50} {-v:12,.2f}")
    profit = sum(acc.values()) - dep
    w.append(f"  {'DRAFT PROFIT / (LOSS) before tax':50} {profit:12,.2f}")
    w.append(f"  (income {inc:,.2f}; expenses {profit - inc:,.2f})\n")
    if bs:
        w.append('## Balance-sheet movements')
        for k, v in sorted(bs.items()):
            w.append(f'  {k:50} {v:12,.2f}')
    w.append(f'\n## {owner} (negative = the business owes the owner)')
    bal = o.get('owner_opening', 0.0)
    w.append(f"  {'Opening balance':50} {bal:12,.2f}")
    for k, v in sorted(own.items(), key=lambda x: x[1]):
        w.append(f'  {k:50} {-v:12,.2f}')  # money the business spent for the owner increases what the owner owes
        bal -= v
    w.append(f"  {'Closing balance':50} {bal:12,.2f}")
    if company and bal > 0:
        w.append('  The director owes the company: interest-free loans can be a deemed dividend (s64E(4)); see the company-tax guide.')
    if ask:
        w.append(f'\n{len(ask)} lines still unanswered (treatment ASK), worth {sum(r["amount"] for r in ask):,.2f}: answer them before relying on this draft.')
    text = '\n'.join(w)
    (workspace.edir(slug) / 'workpapers' / f'{label}-summary.txt').write_text(text + '\n', encoding='utf-8')
    return text, round(profit, 2)
