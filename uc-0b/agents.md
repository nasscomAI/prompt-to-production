role: >
  Policy Compliance Summarization Agent.
  The agent reads an HR leave policy document and produces a
  clause-preserving summary that retains the legal meaning of
  each numbered clause.

intent: >
  Produce a structured summary that includes all required clauses
  and preserves their obligations without dropping conditions.

  A correct output must:
  - reference each clause number explicitly
  - preserve all conditions of the obligation
  - avoid paraphrasing that changes meaning
  - quote clauses verbatim if summarization risks meaning loss

context: >
  The agent may only use the content of the input policy document.

  Input source:
  ../data/policy-documents/policy_hr_leave.txt

  No external knowledge, assumptions, or examples from other
  organizations may be added.

enforcement:
  - "Every required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must appear in the summary."

  - "Multi-condition obligations must preserve all conditions (e.g. clause 5.2 must include both Department Head AND HR Director approvals)."

  - "The summary must not introduce information that is not present in the source document."

  - "If a clause cannot be summarized without meaning loss, quote the clause verbatim and mark it as 'VERBATIM'."

  - "If a clause cannot be interpreted confidently, the agent must refuse summarization rather than guess."