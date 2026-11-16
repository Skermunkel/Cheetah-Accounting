---
name: cheetah-personal-tax
description: South African personal income tax (ITR12) with Cheetah Accounting. Use for IRP5s, medical and retirement annuity certificates, SARS auto-assessments, checking an ITA34, estimating a refund, or preparing what to enter on eFiling for an individual or sole proprietor.
---

# cheetah-personal-tax

1. Call `cheetah_status` for the entity (an "individual" or "sole-proprietor" entity). If the Cheetah tools are
   missing, see the cheetah-init skill.
2. Call `cheetah_guide("personal-tax")` and follow its steps; use `cheetah_guide("documents")` for reading
   certificates and `cheetah_guide("catch-up")` for late years and penalties.
3. Use `cheetah_tax_estimate` for the numbers; never estimate tax tables from memory.
4. Ground rules: `cheetah_guide("ground-rules")`.
