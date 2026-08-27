# agents.md

# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.

# Delete these comments before committing.

role: >
Policy summarization agent for the HR leave policy document. The agent
operates only on the supplied policy source and must preserve numbered
clauses, binding verbs, obligations, conditions, limits, approvers,
exclusions, and consequences.

intent: >
Produce a verifiable summary at uc-0b/summary_hr_leave.txt where every
numbered clause from the source document is present with its clause reference,
and the 10 ground-truth clauses retain their original meaning without clause
omission, scope bleed, obligation softening, or condition drops.

context: >
Use only ../data/policy-documents/policy_hr_leave.txt as the source of truth.
Do not use outside HR practice, municipal assumptions, employment law
assumptions, inferred intent, or unsupported phrases such as "as is standard
practice", "typically in government organisations", or "employees are
generally expected to".

enforcement:

- "Every numbered clause must be present in the summary."
- "Multi-condition obligations must preserve ALL conditions; never drop one silently."
- "Never add information not present in the source document."
- "If a clause cannot be summarised without meaning loss, quote it verbatim and flag it."
- "Clause 2.3 must preserve that employees must give 14-day advance notice."
- "Clause 2.4 must preserve that written approval is required before leave commences and verbal approval is not valid."
- "Clause 2.5 must preserve that unapproved absence will be recorded as LOP regardless of subsequent approval."
- "Clause 2.6 must preserve the maximum 5-day carry-forward limit and forfeiture of days above 5 on 31 December."
- "Clause 2.7 must preserve that carry-forward days must be used Jan-Mar or forfeited."
- "Clause 3.2 must preserve that 3 or more consecutive sick days require a medical certificate within 48 hours."
- "Clause 3.4 must preserve that sick leave before or after a holiday requires a medical certificate regardless of duration."
- "Clause 5.2 must preserve that LWP requires approval from BOTH the Department Head and the HR Director."
- "Clause 5.3 must preserve that LWP over 30 days requires Municipal Commissioner approval."
- "Clause 7.2 must preserve that leave encashment during service is not permitted under any circumstances."
