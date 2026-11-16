# Zoho Books (Free plan) with Claude

Zoho Books is optional. It suits a small business that wants invoices, receipts and reports in one place from now on.
Back years are easier with the bank-statement workflow (`cheetah_guide("bookkeeping")`); only the current year
needs to be in Zoho.

## Plan facts (check on zoho.com/za/books/pricing before relying on them)
- Use the **South Africa edition** (VAT-ready, rand). The Free plan is for small businesses under a yearly revenue
  limit (Zoho's global limit is USD 50,000; the South African limit may differ: check).
- Free plan: 1 user plus an accountant, a yearly invoice limit, add-ons not included. The API allows about 1,000
  calls a day, so post in batches and prefer imports.

## Connect Claude to Zoho Books
1. **Directory connector (try first):** in Claude Desktop, Customize > Connectors > browse, search "Zoho Books",
   Connect, and sign in to Zoho. It has a fixed list of actions; check which ones it offers.
2. **Zoho MCP (only if the directory connector lacks something needed):** create a server at Zoho MCP with Zoho
   Books selected and only the tools needed, then add its URL in Claude as a custom connector. The Free Claude plan
   allows one custom connector, so this uses that slot.
Cheetah's own tools run on the PC and do not use a connector slot.

## Setting up the organisation (once)
- Organisation profile: legal name, registration number, VAT number if registered, financial year start month.
- Chart of accounts: use the account names already in the entity's `rules.json`, so Zoho and the working papers
  match. Add a "Director loan" (or owner's) account as a liability/equity account.
- Bank accounts: add each account (cheque, savings, credit card). Opening balances: from the last finalised
  balance sheet, as at the first day of the first Zoho year.
- Bank feeds: check whether Zoho offers a feed for the bank; otherwise import statements monthly (below).

## Monthly routine
1. Statements: drop the month's CSV or PDF in the inbox, `cheetah_ingest`, then `cheetah_categorise` for the month.
2. `cheetah_zoho_export(entity, label)` writes a CSV. In Zoho: Banking > the account > Import Statement > upload,
   map Date, Description, Reference, Withdrawals and Deposits once. One upload: no Claude usage, no API calls.
3. Categorise in Zoho using the suggested account column; for repeating merchants create Zoho bank rules that
   mirror `rules.json`.
4. Sales: create invoices in Zoho. Costs with slips: Zoho's receipt scanning, or attach the PDF to the transaction.
5. Check: read the month's profit and loss through the connector and compare it with the working-paper totals.
   Explain any difference before moving on.

## Year-end
- Propose journals (depreciation, loan interest, accruals, director salary, private costs to the director's loan)
  as a table: date, accounts, amounts, reason. Post only after the person says yes to that table.
- Reports for the financial statements and ITR14: trial balance, profit and loss, balance sheet from Zoho, checked
  against `cheetah_year_summary`.
- VAT-registered: compare Zoho's VAT return report with the working paper before the person files the VAT201.

## Safety with any connector that can write
- Before every create, update or delete: show exactly what will change (type, date, contact, amounts, accounts) and
  wait for an explicit yes. One confirmation covers only the batch shown.
- Never delete or void anything unless the person asked for that specific item.
- Read before writing: search for an existing contact, invoice or transaction first, to avoid duplicates.
