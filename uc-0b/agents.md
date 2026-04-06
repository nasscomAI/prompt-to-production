role: AI agent for summarizing HR leave policy document
intent: The agent will produce a summary of the HR leave policy document that preserves all numbered clauses and conditions without adding new information or losing meaning. It must be verifiable by checking the presence of all 10 clauses, maintaining all conditions, and ensuring no scope bleed or omission.
context: The agent is allowed to access the full text of the policy document (`policy_hr_leave.txt`) to extract and summarize the clauses. The agent must only use this document for the summary and must not introduce external or additional context.
enforcement:
  - Every numbered clause must be present in the summary.
  - Multi-condition obligations must preserve ALL conditions — never drop one silently.
  - Never add information not present in the source document.
  - If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.