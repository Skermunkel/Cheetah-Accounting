"""Files the person works with outside Claude: review lists to mark up, letters to sign, CSVs for Zoho Books."""
import csv, re
from collections import defaultdict
from . import categorise, workspace
from .simple_pdf import Report


def review_pdf(slug, label, treatment='personal'):
    """Every line of one treatment (default: personal) on paper, with a blank column for the person's notes."""
    e = workspace.entity(slug)
    rows = [r for r in categorise.read(categorise.path_of(slug, label)) if r['treatment'] in (treatment, 'ASK')]
    by = defaultdict(lambda: [0, 0.0])
    for r in rows:
        m = by[categorise.merchant(r['description'])]
        m[0] += 1
        m[1] += r['amount']
    rep = Report(f"{e['name']} - {label}: lines to review")
    for line in [f'These {len(rows)} lines are booked as {treatment.upper()} or not yet answered (ASK).',
                 'Mark any business cost in the last column and say what it was for.',
                 'A business claim needs a slip or invoice, or a signed note explaining why there is none.']:
        rep.text(line)
    rep.heading('Summary by merchant')
    rep.row(['Merchant', 'Count', 'Total (R)', 'Business? / notes'], [42, 7, 13, 40], right={1, 2}, bold=True)
    rep.rule()
    for m, (n, t) in sorted(by.items(), key=lambda x: x[1][1]):
        rep.row([m, n, f'{-t:,.2f}', '_' * 30], [42, 7, 13, 40], right={1, 2})
    rep.heading('All lines (date order)')
    rep.row(['Date', 'Description', 'Amount (R)', 'Business? / notes'], [11, 46, 13, 32], right={2}, bold=True)
    month = ''
    for r in rows:
        if r['date'][:7] != month:
            month = r['date'][:7]
            rep.text(f'--- {month} ---')
        rep.row([r['date'], r['description'], f"{-r['amount']:,.2f}", '_' * 30], [11, 46, 13, 32], right={2})
    out = workspace.edir(slug) / 'out' / f'{label} review list.pdf'
    rep.save(out)
    return out, len(rows)


def letter_pdf(slug, filename, title, body):
    """A letter or note as PDF (and .txt to edit). Dates and signatures stay blank: the person fills them in on the day."""
    rep = Report(title)
    for para in body.split('\n'):
        if para.startswith('## '):
            rep.heading(para[3:])
        else:
            rep.text(para)
    stem = re.sub(r'[^\w .-]', '', filename).strip() or 'letter'
    out = workspace.inside(workspace.edir(slug) / 'out', stem + '.pdf')
    rep.save(out)
    out.with_suffix('.txt').write_text(body + '\n', encoding='utf-8')
    return out


def zoho_bank_csv(slug, label, source=None):
    """Bank lines in a CSV that Zoho Books' "Import Statement" accepts (map the columns once on import).
    Importing statements in one upload costs no Claude usage and no Zoho API calls, unlike posting line by line."""
    rows = categorise.read(categorise.path_of(slug, label))
    if source:
        rows = [r for r in rows if r['source'] == source]
    out = workspace.edir(slug) / 'out' / f'{label} zoho-import{"-" + source if source else ""}.csv'
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Date', 'Description', 'Reference', 'Withdrawals', 'Deposits', 'Suggested account', 'Treatment'])
        for r in rows:
            amt = r['amount']
            w.writerow([r['date'], r['description'], r['source'], f'{-amt:.2f}' if amt < 0 else '',
                        f'{amt:.2f}' if amt > 0 else '', r['account'], r['treatment']])
    return out, len(rows)
