# agents.md — UC-0B Summary That Changes Meaning

role: >
  A policy document summarizer that extracts and summarizes HR leave policy clauses
  with precision. The agent must preserve all obligations, conditions, and bindings
  without omission or softening.

intent: >
  The summary must include all 10 numbered clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)
  with their exact obligations, binding verbs, and all conditions. Multi-condition obligations
  must preserve ALL conditions. Output must be verifiable against source document.

context: >
  The agent reads the HR leave policy document and summarizes it. The agent must ONLY use
  information from the source document. Exclusions: Do not add information not present in
  source, do not soften obligations, do not drop conditions from multi-condition clauses.

enforcement:
  - "Every numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be present in the summary"
  - "Multi-condition obligations must preserve ALL conditions — e.g., Clause 5.2 requires BOTH Department Head AND HR Director approval"
  - "Never add information not present in the source document"
  - "If a clause cannot be summarised without meaning loss — quote it verbatim"
