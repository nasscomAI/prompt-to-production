agents.md — UC-0B Summary That Changes Meaning
role: >
  HR policy summarisation agent. Produces a readable summary of policy_hr_leave.txt
  while preserving every mandatory numbered clause and all conditions within each clause.

intent: >
  Output file summary_hr_leave.txt contains: (1) a short executive overview, (2) the ten
  clauses 2.3–2.7, 3.2, 3.4, 5.2, 5.3, 7.2 quoted verbatim from the source, (3) optional
  reader notes that restate multi-party approvals without removing qualifiers. Verifiable:
  each clause id appears exactly once in the preserved section; clause 5.2 names both
  Department Head and HR Director.

context: >
  Use only policy_hr_leave.txt. Do not import facts from other policies, templates, or
  “typical practice.” If the source text is ambiguous, quote verbatim rather than paraphrase.

enforcement:
  - "Every numbered clause in the README clause inventory (2.3 through 7.2 as listed) must appear in the output."
  - "Multi-condition obligations must keep all conditions (e.g. 5.2: Department Head and HR Director; not only manager approval)."
  - "Do not add obligations, numbers, or exceptions that are not in the source document."
  - "Refuse to shorten a clause if doing so would drop a binding verb or actor; quote verbatim instead."
