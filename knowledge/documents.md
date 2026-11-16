# Documents: getting them in and reading them cheaply

All reading happens on the PC. Claude sees short facts, not whole documents, unless it asks for a piece.

## Ingest
1. The person saves files into `inbox/<entity>` (or the loose `inbox/` and you pass the entity).
   Supported: PDF (digital or scanned), photos (JPG, PNG, TIFF, WEBP), Word, Excel, PowerPoint, HTML, CSV, text.
   Not supported: HEIC phone photos (ask them to share as JPG) and password-protected PDFs (open and "print to PDF").
2. `cheetah_ingest` reads each file, files it under `<entity>/documents/<kind>/`, and returns per document:
   its id, what it is (IRP5, medical certificate, bank statement, invoice, SARS letter...), date range and key facts
   (SARS source codes and amounts on certificates; totals and VAT numbers on invoices; account and balance check on
   statements). Exact duplicates are set aside, not processed twice.
3. Read more only when needed: `cheetah_read(entity, doc, search="3601|3605|4102")` for a few lines, or a slice
   with `start` and `max_chars`.

## How documents are read
- Digital PDFs (most bank statements, invoices, SARS letters): exact text layer. Fast, no AI involved.
- Scans, photos, Word and Excel: Docling (layout, tables and OCR), running locally. The first run downloads its
  models once (`cheetah warm` does this in advance). OCR can misread: check any number that matters against the
  original, especially totals on photos of slips.

## Bank statements
- Every statement is checked: opening balance + all lines = closing balance. `reconciles: true` means no line is
  missing or misread. If false, the result lists the lines where the running balance breaks: read those lines
  in the original and fix by importing a CSV of the same period, or report the format with `cheetah_feedback`.
- Tested on real FNB statements: cheque and savings reconcile line for line; business loans almost always.
  FNB **credit card** PDFs (budget facility and cardholder summaries) do not reconcile yet: use the card's CSV
  export, or report it with `cheetah_feedback`.
- CSV exports from online banking are the most dependable (FNB, Capitec, Absa, Standard Bank and Nedbank all offer
  them). Ask for CSV when a PDF does not reconcile.
- Lines land in `<entity>/transactions/<account>.tsv`. Re-importing the same statement replaces its lines;
  `overlaps_with` warns when two different statements cover the same dates (for example, PDF and CSV of one month):
  keep one.
- Name accounts clearly with `cheetah_import_statement(entity, doc, account="fnb-cheque")` if the automatic name is
  unclear, and keep the same name for every month.

## Certificates (personal tax)
SARS source codes to look for on an IRP5/IT3(a): 3601 salary, 3605 annual payment/bonus, 3606 commission,
3701 travel allowance, 3713 other allowances, 3810 medical aid paid by employer, 4001 pension fund,
4006 retirement annuity, 4005 medical aid contributions, 4102 PAYE deducted, 4141 UIF, 4142 SDL, 4474 employer medical aid contributions.
Codes in the 3600-3999 range are income; 4000-4999 are deductions and tax paid. (check codes against the
SARS "Guide for codes applicable to employees tax certificates" for the year.)
