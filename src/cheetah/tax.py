"""Estimates to check SARS's figures against, not to replace them. Tables are per tax year (year ending end-Feb).

Individual tables: SARS "Rates of tax for individuals" (2023-2026; brackets and rebates unchanged 2024-2026).
A year missing here is not guessed: add it from sars.gov.za with its source first.
"""

BRACKETS = {
    2023: [(226000, 0.18), (353100, 0.26), (488700, 0.31), (641400, 0.36), (817600, 0.39), (1731600, 0.41), (None, 0.45)],
    2024: [(237100, 0.18), (370500, 0.26), (512800, 0.31), (673000, 0.36), (857900, 0.39), (1817000, 0.41), (None, 0.45)],
}
BRACKETS[2025] = BRACKETS[2026] = BRACKETS[2024]
REBATES = {2023: (16425, 9000, 2997), 2024: (17235, 9444, 3145)}
REBATES[2025] = REBATES[2026] = REBATES[2024]
MEDICAL = {2023: (347, 234), 2024: (364, 246)}   # monthly credit: main member and first dependant; each additional
MEDICAL[2025] = MEDICAL[2026] = MEDICAL[2024]
INTEREST_EXEMPT = (23800, 34500)                  # under 65, 65 and older


def bracket_tax(year, taxable):
    tax, lower = 0.0, 0
    for top, rate in BRACKETS[year]:
        part = (min(taxable, top) if top else taxable) - lower
        if part <= 0:
            break
        tax += part * rate
        lower = top or lower
    return tax


def individual(year, age, employment_income=0.0, interest=0.0, other_income=0.0, ra_contributions=0.0,
               medical_contributions=0.0, medical_out_of_pocket=0.0, medical_members=0, medical_months=12,
               paye_paid=0.0, provisional_paid=0.0, disability=False):
    """Income tax for one person for a tax year (e.g. 2025 = 1 Mar 2024 to 28 Feb 2025)."""
    if year not in BRACKETS:
        raise ValueError(f'no tables for {year}: known years {sorted(BRACKETS)}; add them from SARS first')
    notes = []
    exempt = min(interest, INTEREST_EXEMPT[age >= 65])
    income = employment_income + interest - exempt + other_income
    ra = min(ra_contributions, 0.275 * income, 350000)
    if ra < ra_contributions:
        notes.append(f'RA deduction capped at {ra:,.2f}; the excess carries forward')
    taxable = max(income - ra, 0)
    primary, secondary, tertiary = REBATES[year]
    rebate = primary + (secondary if age >= 65 else 0) + (tertiary if age >= 75 else 0)
    main, extra = MEDICAL[year]
    credit = 0.0
    if medical_members:
        credit = medical_months * (main * min(medical_members, 2) + extra * max(medical_members - 2, 0))
    gross = bracket_tax(year, taxable)
    after = max(gross - rebate, 0)
    mtc = min(credit, after)
    add = 0.0  # additional medical expenses credit (s6B)
    if medical_contributions or medical_out_of_pocket:
        if age >= 65 or disability:
            add = 0.333 * (max(medical_contributions - 3 * credit, 0) + medical_out_of_pocket)
        else:
            add = 0.25 * max(max(medical_contributions - 4 * credit, 0) + medical_out_of_pocket - 0.075 * taxable, 0)
    tax = max(after - mtc - add, 0)
    due = tax - paye_paid - provisional_paid
    return {'tax_year': f'{year - 1}-03-01 to {year}-02-28/29', 'taxable_income': round(taxable, 2),
            'interest_exempt': round(exempt, 2), 'ra_deduction': round(ra, 2), 'tax_before_rebates': round(gross, 2),
            'rebates': rebate, 'medical_scheme_credit': round(mtc, 2), 'additional_medical_credit': round(add, 2),
            'tax': round(tax, 2), 'paye_and_provisional_paid': round(paye_paid + provisional_paid, 2),
            'estimated_refund' if due < 0 else 'estimated_payable': round(abs(due), 2), 'notes': notes,
            'caution': 'estimate only: SARS assessment (ITA34) is what counts; differences point at missing certificates or codes'}


def company(year_end, taxable_income):
    """Flat company rate: 28% for years ending before 31 March 2023, 27% after. Small business corporations differ."""
    rate = 0.28 if year_end < '2023-03-31' else 0.27
    return {'rate': rate, 'tax': round(max(taxable_income, 0) * rate, 2),
            'caution': 'standard company rate; a qualifying small business corporation (s12E) pays less; check eligibility'}
