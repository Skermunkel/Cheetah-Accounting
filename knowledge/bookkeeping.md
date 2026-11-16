# Bookkeeping from bank statements (any business, any year)

This is how back years are caught up, and how a year without bookkeeping software is done.
For years kept in Zoho Books, see `cheetah_guide("zoho-books")`.

## The loop
1. **Statements in**: every month of the financial year, every account the business used (cheque, savings,
   credit card, loan). `cheetah_status` shows each account's date range: look for gaps.
2. **Categorise**: `cheetah_categorise(entity, start, end, label)` with the financial year's dates, e.g.
   start 2024-03-01, end 2025-02-28, label "FY2025". It returns totals and a list of unanswered merchants.
3. **Ask, then record**: go through the questions merchant by merchant, biggest first. For each answer, call
   `cheetah_rule` with the reason in the person's words. Group obvious ones ("all of Checkers, Spar and Woolworths
   are private"). Use `dates` or `amount` in a rule for a one-off exception.
4. **Repeat** step 2 until `unanswered_lines` is 0 (or the rest is marked personal with the person's agreement).
5. **Paper review** (optional, good for long lists): `cheetah_review_pdf` makes a list of personal and unanswered
   lines; the person marks business items by hand; you turn their marks into rules.
6. **Year summary**: `cheetah_year_summary` gives the draft income statement and owner/director account.
   Add what is not on the bank in `workpapers/<label>.json` (opening loan balance, depreciation, loan interest
   journals, salary): see the tool's description.

## Treatments
- `income`: sales and other income of the business. `expense`: a business cost; use `share` for mixed use
  (e.g. 0.2 of home rent for a home office), the rest goes to the owner.
- `personal`: a private cost paid from the business account, or owner money paid in. For a company this is the
  director's loan account, never an expense.
- `transfer`: between the business's own accounts (counts nowhere). `loan`: loans received or repaid (not income).
- `capital`: money put in by the owner as capital or a gift (not income). `asset`: equipment that lasts more than a
  year (depreciated over its life, not expensed at once, unless small: under R7,000 per item can be written off
  in full).
- `tax`: payments to SARS (not an expense). `salary`: salary to the director or staff (needs PAYE registration).

## Mixed-use costs (home office, vehicle, phone)
Use a fair, explainable share and write down how it was worked out:
- Home office: floor area of the office room over the home's total area, applied to rent, electricity, insurance.
- Vehicle: business kilometres over total kilometres, from a logbook. Without a logbook, use a conservative
  estimate from the usual weekly business trips, put it in a signed note, and keep a logbook from now on.
- Groceries, clothes, personal meals and family costs are never business costs.

## Costs without slips
List them in a director's/owner's note: date, amount, what it was for, who was there (meetings), why there is
no slip, and the share claimed. The person signs and dates it on the day they sign it.
`cheetah_save_letter` makes the PDF; leave the signature and date lines blank.

## Related businesses
Shared costs, joint projects and loans with another business must appear in both sets of books with the same
amounts: a cost one business pays for the other is a recharge (or loan), not its own expense. Note the other
business's name in the rule and ask for its figures before finalising.
