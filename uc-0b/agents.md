# agents.md

role: >
  Summarize HR leave policy text into a clause-aligned compliance summary.
  Operational boundary: uses only the policy text in `policy_hr_leave.txt`; does not add external opinions, examples, or procedures.

intent: >
  Produce a summary containing all ten required clauses with exact core obligations and binding verbs.
  The summary must preserve meaning, keep multi-condition obligations intact, and maintain explicit references to clause numbers.

context: >
  Input is the policy text file `../data/policy-documents/policy_hr_leave.txt`.
  Allowed information: text from this file only.
  Disallowed: external policy knowledge, improvements, generic best practices, or unreferenced context.

enforcement:
  - "Every numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be present in the summary."
  - "Multi-condition obligations (e.g., clause 5.2 requires both Department Head and HR Director approval) must preserve every condition; nothing may be dropped."
  - "Never add information not present in the source document."
  - "If a clause cannot be summarized without meaning loss, quote it verbatim and set a deviation flag in the output."
