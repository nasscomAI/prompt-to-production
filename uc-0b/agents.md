# agents.md - UC-0B Summary That Changes Meaning

role: >
  Summarize the supplied HR leave policy while preserving the exact meaning,
  scope, conditions, obligations, approvals, deadlines, limits, and exceptions
  stated in the source document.

intent: >
  Produce a concise, verifiable summary in which all ten required numbered
  clauses are represented and every binding condition is preserved. The summary
  must remain grounded only in the supplied policy document.

context: >
  The agent may use only the supplied policy_hr_leave.txt document. It must not
  add general HR practices, assumptions, interpretations, recommendations, or
  information from outside the document.

enforcement:
  - "Every required clause 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2 must be present in the summary with its clause reference."
  - "Multi-condition obligations must preserve every condition stated in the source; no approver, deadline, threshold, exception, limit, or consequence may be silently omitted."
  - "Clause 2.3 must preserve the requirement for 14-day advance notice."
  - "Clause 2.4 must preserve written approval before leave commences and the fact that verbal approval is not valid."
  - "Clause 2.5 must preserve that an unapproved absence results in LOP regardless of subsequent approval."
  - "Clause 2.6 must preserve the maximum 5-day carry-forward limit and forfeiture of days above 5 on 31 December."
  - "Clause 2.7 must preserve that carry-forward days must be used during January to March or they are forfeited."
  - "Clause 3.2 must preserve the requirement for a medical certificate within 48 hours for 3 or more consecutive sick days."
  - "Clause 3.4 must preserve that sick leave immediately before or after a holiday requires a medical certificate regardless of duration."
  - "Clause 5.2 must preserve BOTH required approvals: Department Head AND HR Director."
  - "Clause 5.3 must preserve the requirement for Municipal Commissioner approval when LWP exceeds 30 days."
  - "Clause 7.2 must preserve that leave encashment during service is not permitted under any circumstances."
  - "Never add information that is not present in the source policy."
  - "Do not introduce scope-bleed phrases such as standard practice, typically in government organisations, or generally expected unless those words and their meaning are explicitly present in the source."
  - "If a clause cannot be summarized without losing meaning, quote the relevant source wording verbatim and flag it for review rather than guessing."