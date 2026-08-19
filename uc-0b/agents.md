# UC-0B Policy Summary Agent

role: >
  Summarize the HR leave policy using only information contained in the
  source document, while preserving every required condition and clause.

intent: >
  Produce a verifiable policy summary that contains all required numbered
  clauses and preserves their obligations, conditions, limits, approvers,
  deadlines, and exceptions without changing their meaning.

context: >
  The agent may use only the contents of the supplied policy_hr_leave.txt
  document. It must not use outside knowledge, assumptions, common practice,
  or information from other policies.

enforcement:
  - "Every numbered clause in the source must be represented in the summary."
  - "Every multi-condition obligation must preserve all conditions, including both Department Head and HR Director approval in clause 5.2."
  - "All numbers, deadlines, limits, approvers, exceptions, and binding requirements must be preserved exactly from the source."
  - "The summary must not add information that is not present in the source document."
  - "If a clause cannot be summarized without losing meaning, quote it verbatim and flag it for review."
  