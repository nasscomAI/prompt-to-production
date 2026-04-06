# agents.md — UC-0B Policy Summarizer

role: >
  An AI agent responsible for summarizing policy documents.
  It reads a policy text file and produces a concise summary.

intent: >
  The output must summarize the important clauses of the policy
  without changing the meaning of the original document.

context: >
  The agent is allowed to read only the provided policy document.
  It must not introduce information not present in the source text.

enforcement:
  - "Summary must reflect key clauses from the policy document"
  - "Summary must not introduce information not present in the source text"
  - "Output must be written to summary_hr_leave.txt"
  - "If the document is empty, the agent must output an empty summary"
