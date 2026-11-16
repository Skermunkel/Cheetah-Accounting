# Company tax (ITR14), financial statements and CIPC

## Each financial year, in this order
1. **Books**: bank lines categorised and every question answered (`cheetah_guide("bookkeeping")`), or Zoho Books
   reports for the year.
2. **Year summary**: `cheetah_year_summary`. Add the items not on the bank in `workpapers/<label>.json`: opening
   director loan, depreciation, loan interest and fees, director salary.
3. **Financial statements (AFS)**: income statement, balance sheet, notes, director's report. An owner-managed
   company (every shareholder is a director) needs no audit or independent review in most cases (Companies Act
   s30(2A)); the AFS still have to be prepared and approved by the director. (check: public interest score)
4. **Tax computation**: start from the accounting profit, then
   - add back what tax does not allow: entertainment, fines and penalties, SARS interest, private costs, accounting
     depreciation (replaced by wear-and-tear allowances: SARS Interpretation Note 47; small items under R7,000 may be
     written off in full);
   - assessed losses from earlier years reduce the taxable income;
   - rate (`cheetah_company_tax`): 28% for years ending before 31 March 2023, 27% after. A qualifying small business
     corporation (s12E: turnover up to R20 million, all shareholders natural persons, other conditions) pays lower
     rates on the first part of its income. (check the current SBC table)
5. **ITR14**: the person (as public officer) completes it on eFiling from a "what to enter" sheet, with the AFS
   attached where asked. Due within 12 months after the year-end.
6. **Provisional tax**: companies are provisional taxpayers (IRP6 at 6 and 12 months into the year).

## Director's loan account
- Private costs paid by the company and money the director puts in run through this account.
- If the **director owes the company** and pays no interest (or low interest), the benefit can be a deemed
  dividend (s64E(4)): dividends tax at 20% on interest at the official rate. Options: repay, pay interest, or
  declare salary or a dividend to clear it. Raise it with the person every year-end.
- If the **company owes the director**, no tax arises on the loan itself; keep a simple loan agreement.

## Director's salary
Paying a salary needs PAYE registration and monthly EMP201 returns (`cheetah_guide("vat-paye")`). Private costs can
be treated as salary only if they run through payroll. Compare: salary (personal tax, deductible for the company)
versus loan or dividend; show the numbers and let the person decide.

## CIPC (each year)
- **Annual return**: within 30 business days after the anniversary of incorporation, on BizPortal or CIPC
  eServices. Late returns cost more; two or more years unfiled can lead to deregistration.
- **Beneficial ownership (BO) declaration**: on the CIPC BO portal; CIPC may block the annual return until it is filed.
- Dormant companies still file both, and still file an ITR14 (short dormant version).

## Records the company must keep
Accounting records for 7 years (Companies Act s24, s28); tax records for 5 years after the return (Tax
Administration Act s29). No specific software is required.
