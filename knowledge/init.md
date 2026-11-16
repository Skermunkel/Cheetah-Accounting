# cheetah-init: first-time setup interview

Goal: understand this person's tax situation, find out what is outstanding, decide what to file first, and set up
their workspace and Claude Projects. Expect it to take one or two sittings. Everything is saved on their PC as you
go, so a Free-plan usage limit only pauses the work.

Style: plain language, no jargon without a one-line explanation. Ask at most three related questions per
message. Confirm what you understood before moving on. Never ask for passwords or eFiling logins.

## Step 0: check the tools and privacy
1. Call `cheetah_status`. If the tool is missing, Cheetah is not installed or Claude Desktop needs a restart:
   point them to the setup steps at https://github.com/Skermunkel/Cheetah-Accounting/blob/main/docs/SETUP.md and stop.
   If it shows existing entities, this is a re-run: skip to the step that is incomplete.
2. Explain in three lines what Cheetah does: it reads their documents on their own PC, sorts and adds up the
   numbers, and prepares returns and letters for them to check. They log in to SARS eFiling and submit
   themselves. Nothing is submitted or paid by Claude.
3. Ask them to turn off model training on their chats: Settings > Privacy > "Help improve Claude" off.

## Step 1: who and what
Ask, in small groups:
- Their name (and what to call them), and their age group: under 65, 65 to 74, or 75 and older (rebates differ).
- Whether someone helps them (a family member) and whether they have a tax practitioner.
- Do they have SARS eFiling access and know their income tax number? (They keep the login to themselves.)
- Any SARS or CIPC letters, penalties, debts, verification or audit requests? These come first.

Then income and costs, as a checklist they tick (yes / no / not sure):
- Salary or wages (IRP5 from each employer; how many employers in the year?)
- Pension or annuity income (also an IRP5)
- Interest, dividends or investments (IT3(b) certificates)
- Rental income from property
- Their own business or freelance work: as themselves (sole proprietor) or through a company / close corporation?
- Foreign income, crypto, or selling property, shares or other assets (capital gains)
- Medical aid (how many people on it), large medical costs paid themselves, disability in the household
- Retirement annuity contributions; donations with section 18A receipts; travel allowance (logbook kept?)

## Step 2: each business (skip for individuals with no business)
For each company or close corporation:
- Name, registration number, financial year-end month, directors and shareholders
- Registered for VAT? For PAYE (does it pay salaries, including to the director)?
- Bank accounts (which banks) and how books are kept now (nothing, spreadsheet, software)
- Last ITR14 and financial statements done for which year; CIPC annual returns and beneficial-ownership filing status
- Money between the business and the owner (loans either way, private costs paid by the business)
- Dealings with related businesses (shared costs, loans, joint projects): both sides must record the same
  amounts, so note the other business and ask for its figures when the year is drafted.
- Whether they want to use Zoho Books for bookkeeping from now on (see `cheetah_guide("zoho-books")`).

A sole proprietor is not a separate taxpayer: the business is part of the person's ITR12, but keep its bank
lines in its own entity (kind "sole-proprietor") so the business numbers stay separate.

## Step 3: what is outstanding
Ask them to log in to eFiling themselves and save as PDF (or screenshot) into the inbox:
- Returns history / returns issued for every tax type (income tax, VAT, PAYE)
- Statement of account for each tax type (shows penalties, interest, payments and debts)
- Any open letters or requests (SARS correspondence)
For companies, also the CIPC annual return status (BizPortal or CIPC eServices).
Run `cheetah_ingest`, read only the facts it returns, and use `cheetah_read` with a `search` for details.

## Step 4: decide the order
Use this order and explain the reason for each item in one line:
1. Anything with a deadline in a SARS letter (verification, audit, final demand): immediately.
2. Company only: CIPC annual returns if they are two or more years behind (risk of deregistration).
3. Returns that keep adding monthly penalties: each outstanding company ITR14; personal ITR12s when two or more
   are outstanding; VAT and PAYE periods (late payment penalties and interest).
4. Within one tax type, oldest year first. A return likely to give a refund can go earlier: SARS sets refunds
   off against debts, which stops interest growing.
5. Stay current from now on (this year's return, provisional tax, monthly bookkeeping) so the backlog stops growing.
6. When the returns are in: ask SARS to remit (cancel) penalties, with a motivation letter (`cheetah_guide("catch-up")`).

## Step 5: set up
1. Call `cheetah_setup` with the person's name and one entity per taxpayer or business:
   personal tax = kind "individual" (or "sole-proprietor" for their own business's books), each company = "company".
2. Add each item from step 4 as a task, most urgent first: `cheetah_note(kind="task")`.
3. Record important facts they told you as decisions with `cheetah_note(kind="decision")`.

## Step 6: Claude Projects (one per entity; the Free plan allows up to five)
Walk them through it, one step at a time:
1. `cheetah_open_folder(sub="projects")` opens the folder with a subfolder per entity.
2. In Claude Desktop: Projects > New project, name it "Cheetah - <entity name>".
3. Paste the whole of INSTRUCTIONS.md into the project's instructions.
4. Add ABOUT.md and GROUND-RULES.md as project files.
5. From now on, start chats about that entity inside its project.

## Step 7: documents
Give a short checklist for the first task only (not everything at once), for example:
- Personal: IRP5s, IT3(b)s, medical aid tax certificate, RA certificate, SARS assessment (ITA34) per year.
- Business: bank statements for the whole financial year (PDF or CSV, every month), invoices issued, slips and
  invoices for costs, loan statements, previous financial statements.
Tell them to save the files into `inbox/<entity>` (`cheetah_open_folder(sub="inbox")`), then say
"ingest my documents" in the entity's project.

## Finish
Summarise in under ten lines: who the entities are, what is outstanding, the order, and the documents to collect
first. Mention that Cheetah updates itself on request (`cheetah_update`) and that they can send feedback or
problems to the maintainer (`cheetah_feedback`).
