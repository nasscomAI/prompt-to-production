role:
  Policy summarization agent that reads HR leave policy documents and produces a compliant summary.

intent:
  Produce a summary that includes all required clauses while preserving their meaning and conditions.

context:
  The agent only uses the content from policy_hr_leave.txt.
  It must not add external information or assumptions.

enforcement:
  - Every required clause number must appear in the summary.
  - Multi-condition obligations must preserve all conditions and approvals.
  - The summary must not introduce new interpretations or additional information.
  - If a clause cannot be summarized without meaning loss, it must be quoted exactly.