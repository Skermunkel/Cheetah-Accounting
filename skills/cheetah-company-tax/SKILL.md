---
name: cheetah-company-tax
description: South African company compliance with Cheetah Accounting. Use for a (Pty) Ltd or close corporation's financial statements, ITR14, director's loan account, director salary and PAYE, VAT201, CIPC annual returns and beneficial ownership, late returns and penalty remission letters.
---

# cheetah-company-tax

1. Call `cheetah_status` for the company entity. If the Cheetah tools are missing, see the cheetah-init skill.
2. Call `cheetah_guide("company-tax")` and follow it. Books first (`cheetah_guide("bookkeeping")` or
   `cheetah_guide("zoho-books")`), then the year summary, AFS, tax computation and ITR14 sheet.
3. VAT and PAYE: `cheetah_guide("vat-paye")`. Late returns and relief: `cheetah_guide("catch-up")`.
4. Ground rules: `cheetah_guide("ground-rules")`.
