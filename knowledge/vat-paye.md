# VAT and PAYE

## VAT (only if the business is registered)
- Registration: compulsory once taxable sales pass the threshold in 12 months (R1 million for many years; an
  increase has been announced: check the current figure); voluntary from R50,000.
- VAT201 every two months for most small vendors (category A or B), due by the 25th after the period (the last
  business day for eFiling payments). (check the vendor's category on eFiling)
- **Output VAT**: 15/115 of standard-rated sales. Exports of goods and many services to foreign clients are
  zero-rated (0%, but still declared).
- **Input VAT**: only with a valid tax invoice in the business's name (and VAT number for invoices over R5,000).
  No input VAT on entertainment, on private costs, or on purchases from non-vendors. Missed input VAT can be claimed
  in a later return within 5 years (s16(3)).
- From `cheetah_categorise`: rules with `vat: standard` feed the period's VAT summary; check each input VAT line
  has its tax invoice before including it.
- Late payment: 10% penalty plus interest. Late returns: SARS may also levy penalties. File even when nothing is due.

## PAYE (if the company pays any salary, including to the director)
- Register as employer on eFiling before the first salary that is above the tax threshold, or as soon as one
  employee earns above it.
- EMP201 every month, paid by the 7th of the next month: PAYE, UIF (1% + 1%), SDL (only if payroll exceeds
  R500,000 a year).
- EMP501 reconciliation twice a year, and IRP5 certificates for each employee after the tax year.
- A director's salary may be paid as one amount a year; PAYE is still worked out on the full year.

## Turnover tax (micro businesses, alternative)
Sole proprietors and small companies with turnover up to R1 million may elect turnover tax instead of income tax
and VAT (low rates on turnover, one simple return). Worth comparing for a very small business. (check eligibility)
