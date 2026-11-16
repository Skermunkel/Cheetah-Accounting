# Personal income tax (ITR12)

Tax year: 1 March to the end of February. "Tax year 2025" = 1 March 2024 to 28 February 2025.

## Does the person have to file? (check SARS's notice for the year)
Generally yes if any of these apply: income from more than one employer in the year; employment income above the
amount in SARS's annual notice (R500,000 in recent years); any income not taxed through PAYE (business, freelance,
rental, foreign); interest above the exemption; capital gains above the annual exclusion; SARS asked them to.
If unsure, filing is safer than not filing. SARS's auto-assessment (sent mid-year to many people) counts as filed
only if it is correct and complete.

## Steps for each year
1. Gather: IRP5/IT3(a) from each employer or pension fund; IT3(b) for interest and dividends; medical aid tax
   certificate; RA certificate; section 18A receipts; SARS assessment (ITA34) if one was issued.
   For business or rental income: the income and costs for the year (bookkeeping guide).
2. `cheetah_ingest`; check the source codes and totals it lists.
3. Compare with SARS: on eFiling the return for that year is usually pre-filled from employers, medical aids and
   banks. Ask the person to save the pre-filled return (or auto-assessment) as PDF into the inbox. Compare every
   amount with the certificates; list what is missing or different.
4. Estimate with `cheetah_tax_estimate` (tables 2023-2026 built in) and explain the expected refund or amount due.
   A big difference from SARS's figure means something is missing: find it before filing.
5. Prepare a one-page "what to enter" sheet per return section (`cheetah_save_letter`): the person fills in the
   eFiling return from it, checks, and submits.
6. After filing: save the ITA34 into the inbox; note the outcome (`cheetah_note`); refunds take a few weeks;
   SARS may ask for supporting documents (verification): reply with exactly what is requested.

## Common items
- **Interest**: exempt up to R23,800 a year (R34,500 at 65 or older); the rest is taxable.
- **Medical**: medical scheme fees credit per month for each person on the scheme; additional credit for high
  out-of-pocket costs and for anyone 65+ or with a disability (keep receipts; disability needs the ITR-DD form).
- **Retirement annuity**: deductible up to 27.5% of income, capped at R350,000 a year.
- **Travel allowance**: a deduction needs a logbook of business trips.
- **Home office** for employees: strict conditions (mostly working from a dedicated room); usually not available.
- **Business or freelance income** (sole proprietor): declared on the ITR12 with the costs; the person also becomes
  a provisional taxpayer (two payments a year, IRP6, end of August and end of February).
- **Pensioners**: the secondary rebate applies from 65, tertiary from 75. Several pensions or a pension plus other
  income often means tax is due because each payer deducted too little.

## Rates (from `cheetah_tax_estimate`)
Brackets, rebates and medical credits for tax years 2023 to 2026 are built in. For later years the tool refuses
until the maintainer adds the official tables; do not estimate them from memory.

## Get a practitioner for
Estates, foreign income or emigration, large capital gains, disputes or audits, trusts.
