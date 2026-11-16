# Cheetah Accounting

A local helper for South African personal and small-business tax, used through the **Claude Desktop** app, and
designed to work on the **Free** plan.

Cheetah reads your documents on your own computer (bank statements, IRP5s, certificates, invoices, photos of
slips), sorts and adds them up, and gives Claude short summaries to work with. Claude then asks you the questions
that matter, keeps a record of every decision, and prepares returns, schedules and letters **for you to check and
submit yourself** on SARS eFiling or CIPC. Nothing is submitted or paid by Claude.

**Start here: [docs/SETUP.md](docs/SETUP.md).** To have Claude guide the setup, use [docs/HANDOFF-PROMPT.md](docs/HANDOFF-PROMPT.md).

## What it covers
- Personal income tax (ITR12): certificates, auto-assessment checks, refund estimates (tax years 2023-2026)
- Sole proprietors and companies: bank statements to categorised books, year summary, director's loan, ITR14 and
  financial statements preparation, VAT201 and PAYE basics, CIPC annual return and beneficial ownership
- Catching up: what to file first, penalty remission requests and motivation letters
- Optional bookkeeping in **Zoho Books** (Free plan) through Claude's Zoho Books connector

## How it fits together

| Part | Where it runs | What it does |
|---|---|---|
| `src/cheetah/` (MCP server) | your computer | reads documents (pdfplumber, Docling), parses statements, applies rules, writes working papers, PDFs, CSVs |
| `knowledge/` guides | served by the MCP server | the process and SA tax reference, read by Claude only when needed |
| `skills/` | uploaded to Claude | thin entry points (cheetah-init and others) that load the guides from the installed version |
| Claude Project per taxpayer | Claude Desktop | instructions and a short profile; live state comes from `cheetah_status` |
| Zoho Books connector | Claude (optional) | invoices, reports and year-end journals for businesses that use Zoho |
| `Cheetah/workspace/` | your computer | your documents, transactions, decisions and outputs; never in this repo |

**Why the work happens locally:** the Free plan has usage limits. Reading a 20-page statement in a chat uses far
more than a 10-line summary of it. Cheetah does the reading and arithmetic on your computer, checks every
statement against its opening and closing balances, and sends Claude only what it needs to decide or ask.

**Document reading:** digital PDFs use their exact text layer (no AI model, no mistakes). Scans, photos, Word
and Excel files use [Docling](https://github.com/docling-project/docling) (MIT licence), which runs fully offline
after a one-time model download and handles tables and OCR.

**Updates:** the skills only point at the guides; the guides and tools come from the installed copy of this
repo. Asking Claude to "update Cheetah" pulls the latest version, so improvements reach everyone without
re-uploading skills.

## Privacy
- Documents and records stay in `Cheetah/workspace` on your computer. Only the summaries you discuss in a chat
  go to Claude. Turn off "Help improve Claude" in Settings > Privacy.
- Feedback (`cheetah_feedback`) opens a GitHub issue for you to read before submitting; ID, tax and account
  numbers, emails, phone numbers and amounts are masked.

## Not tax advice
Cheetah helps you prepare. Tax rules change every year; check figures marked "(check)" on sars.gov.za, and use a
registered tax practitioner for audits, disputes, estates, trusts or foreign income.

## Development
```
uv sync
uv run pytest
uv run cheetah doctor
```
Add a bank format: put an anonymised statement text in `tests/fixtures/`, make `statements.py` parse it, and add
a test that it reconciles. Add a tax year: extend the tables in `tax.py` with the SARS source in the docstring.

Licence: MIT.
