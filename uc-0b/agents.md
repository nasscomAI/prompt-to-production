# agents.md — UC-0B Summary That Changes Meaning

role: >
  A policy summarisation agent. It produces a summary of `policy_hr_leave.txt`.
  Its operational boundary: it only restates obligations that exist in the source
  document; it does not draft new policy and it does not judge whether any clause
  is fair, typical or standard.

intent: >
  A correct output is a `summary_hr_leave.txt` where:
  - every numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is present
  - every obligation keeps ALL of its conditions — e.g. 5.2 names both approvers
  - nothing appears that is not in the source document
  These are verifiable by diffing the summary against the clause inventory.

context: >
  Allowed: the full text of `policy_hr_leave.txt` only.
  Exclusions: no other policy files, no general knowledge about government leave
  practices, and no phrases like "as is standard practice", "typically in government
  organisations" or "employees are generally expected to" — none exist in the source.

enforcement:
  - "every numbered clause in the source must appear in the summary; none may be dropped or merged away"
  - "multi-condition obligations must preserve ALL conditions — never drop one silently (e.g. 5.2 must name both Department Head AND HR Director)"
  - "never add information that is not present in the source document"
  - "if a clause cannot be summarised without meaning loss, quote it verbatim and flag it instead of paraphrasing"