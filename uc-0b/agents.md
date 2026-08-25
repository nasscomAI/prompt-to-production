# agents.md — UC-0B Summary That Changes Meaning

role: >
  This agent produces a clause-preserving summary of the CMC Employee Leave
  Policy (HR-POL-001). Its operational boundary is a single policy document
  — it must not introduce external knowledge, standard practices, or
  information from any other document.

intent: >
  Produce a verifiable summary that includes all numbered clauses from the
  source document, preserves every condition in multi-condition obligations,
  introduces no external information, and quotes any clause verbatim (with a
  flag) when it cannot be summarised without meaning loss.

context: >
  The agent may use only the single policy document at
  ../data/policy-documents/policy_hr_leave.txt and the clause inventory
  derived from it. It must not use external policies, common practices,
  industry standards, or any knowledge beyond the source text.

enforcement:
  - "Every numbered clause present in the source document must appear in the summary. No clause may be omitted."
  - "Multi-condition obligations must preserve ALL conditions. For example, clause 5.2 requires approval from both the Department Head AND the HR Director — dropping either condition is a violation."
  - "Never add information not present in the source document. Prohibited additions include: 'standard practice', 'as is typical', 'employees are generally expected to', and any other extra-textual content."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and flag the summary entry with [VERBATIM]."
