import json
from pathlib import Path
import pytest

FIX = Path(__file__).parent / 'fixtures'


@pytest.fixture
def wsdir(tmp_path, monkeypatch):
    monkeypatch.setenv('CHEETAH_WORKSPACE', str(tmp_path / 'ws'))
    return tmp_path / 'ws'


def test_fnb_text_reconciles_and_signs_from_balance():
    from cheetah import statements
    rows, chk = statements.parse_text((FIX / 'fnb-statement.txt').read_text())
    assert [r['amount'] for r in rows] == [2500.0, -450.25, -99.0, -1200.0, -750.75]
    assert rows[0]['date'] == '2023-12-05' and rows[-1]['date'] == '2024-01-15'  # year from the statement period
    assert chk['reconciles'] is True and chk['opening'] == 1000.0


def test_text_without_balance_breaks_are_reported():
    from cheetah import statements
    text = (FIX / 'fnb-statement.txt').read_text().replace('750.75        1,000.00 Cr', '705.75        1,000.00 Cr')
    rows, chk = statements.parse_text(text)
    assert chk['reconciles'] is False and chk['check_lines']


def test_csv_debit_credit_columns():
    from cheetah import statements
    rows, chk = statements.parse_csv((FIX / 'capitec.csv').read_text())
    assert [r['amount'] for r in rows] == [15000.0, -845.5, -2900.0]
    assert chk['opening'] == 500.0 and chk['reconciles'] is True


def test_categorise_summary_and_year(wsdir):
    from cheetah import server, books
    server.cheetah_setup('Test Person', [{'name': 'Test Shop', 'kind': 'company', 'year_end': '02'}])
    inbox = wsdir / 'inbox' / 'test-shop'
    (inbox / 'dec-jan.txt').write_text((FIX / 'fnb-statement.txt').read_text())
    res = json.loads(server.cheetah_ingest())
    doc = res['documents'][0]
    assert doc['what'] == 'bank or card statement' and doc['statement']['reconciles'] is True
    server.cheetah_rule('test-shop', 'Inward Swift', 'income', 'Sales - exports', 'exports', vat='zero')
    server.cheetah_rule('test-shop', 'Engen', 'expense', 'Motor expenses', '25% business use estimate', share=0.25)
    s = json.loads(server.cheetah_categorise('test-shop', '2023-03-01', '2024-02-29', 'FY2024'))
    assert s['lines'] == 5
    assert [q['merchant'] for q in s['questions']] == ['Rent Office']   # Checkers (starter rule) and fee are known
    text, profit = books.year('test-shop', 'FY2024')
    assert profit == round(2500 - 99 - 750.75 * 0.25, 2)
    assert 'Director loan' in text and 'still unanswered' in text
    assert (wsdir / 'projects' / 'test-shop' / 'INSTRUCTIONS.md').read_text().count('test-shop') >= 1
    server.cheetah_note('test-shop', 'task', 'File ITR14 FY2024')
    assert 'File ITR14 FY2024' in server.cheetah_status('test-shop')
    out = server.cheetah_zoho_export('test-shop', 'FY2024')
    assert out.startswith('5 lines')
    assert 'lines ->' in server.cheetah_review_pdf('test-shop', 'FY2024')


def test_duplicate_documents_are_set_aside(wsdir):
    from cheetah import server
    server.cheetah_setup('P', [{'name': 'Me', 'kind': 'individual'}])
    for n in ('a.csv', 'b.csv'):
        (wsdir / 'inbox' / 'me' / n).write_text((FIX / 'capitec.csv').read_text())
    res = json.loads(server.cheetah_ingest('me'))
    assert sum('duplicate_of' in d for d in res['documents']) == 1


def test_workspace_paths_cannot_escape(wsdir):
    from cheetah import workspace
    with pytest.raises(ValueError):
        workspace.inside(workspace.root(), '../outside')


def test_individual_tax_2025():
    from cheetah import tax
    r = tax.individual(2025, 40, employment_income=300000, paye_paid=40000)
    assert r['tax_before_rebates'] == pytest.approx(42678 + 0.26 * (300000 - 237100))
    assert r['tax'] == pytest.approx(r['tax_before_rebates'] - 17235)
    assert r['estimated_payable'] == pytest.approx(r['tax'] - 40000)
    with pytest.raises(ValueError):
        tax.individual(2031, 40)


def test_medical_credit_and_interest_exemption():
    from cheetah import tax
    r = tax.individual(2024, 70, employment_income=200000, interest=30000, medical_members=2)
    assert r['interest_exempt'] == 30000 and r['rebates'] == 17235 + 9444
    assert r['medical_scheme_credit'] == min(12 * 2 * 364, r['tax_before_rebates'] - r['rebates'])


def test_redaction():
    from cheetah import upkeep
    s = upkeep.redact('ID 8001015009087, tax 0123456789, acc 62000001234, R1,234.56, me@x.co.za')
    assert '8001015009087' not in s and '0123456789' not in s and '62000001234' not in s and 'R1,234.56' not in s
    assert '@' not in s


def test_extract_kind_and_irp5_codes():
    from cheetah import extract
    t = 'IRP5 Employee tax certificate 2025\n3601 Income taxable 250 000.00\n4102 PAYE 30 000.00\n'
    kind, _ = extract.kind_of(t, 'irp5.pdf')
    assert kind == 'certificates'
    assert extract.facts(t, kind)['source_codes'] == {'3601': 250000.0, '4102': 30000.0}


def test_fnb_bare_debits_amounts_in_descriptions_and_fee_column():
    from cheetah import statements
    rows, chk = statements.parse_text((FIX / 'fnb-overdraft.txt').read_text())
    assert [r['amount'] for r in rows] == [1500.0, -109.99, -5.52, -428.17, 158.03]
    assert rows[1]['description'].startswith('POS Purchase 109.99 Google')
    assert chk['reconciles'] is True and chk['opening'] == -5109.48


def test_loan_balance_only_lines_are_skipped():
    from cheetah import statements
    rows, chk = statements.parse_text((FIX / 'loan.txt').read_text())
    assert [r['amount'] for r in rows] == [-265.61, -69.0, 537.61]
    assert chk['reconciles'] is True
