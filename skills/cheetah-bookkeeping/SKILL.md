---
name: cheetah-bookkeeping
description: Bookkeeping with Cheetah Accounting. Use when the person adds bank statements, slips or invoices, wants transactions categorised, asks what a payment was, needs a year summary, a list of private transactions to review, a note for costs without slips, or wants to work in Zoho Books.
---

# cheetah-bookkeeping

1. Call `cheetah_status` for the entity. If the Cheetah tools are missing, see the cheetah-init skill.
2. New documents: `cheetah_ingest`, then report only the facts and any statement that does not reconcile.
3. Follow `cheetah_guide("bookkeeping")`: categorise, ask about unanswered merchants biggest first, record each
   answer with `cheetah_rule`, repeat, then `cheetah_year_summary`.
4. Zoho Books: follow `cheetah_guide("zoho-books")`. Before any write through a Zoho connector, show exactly what
   will change and wait for a clear yes.
5. Ground rules: `cheetah_guide("ground-rules")`.
