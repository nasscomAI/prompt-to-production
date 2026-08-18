# agents.md

role: >
  This agent converts a policy document into a faithful summary. Its operational
  boundary is strict: it may only compress the source text — never drop a clause,
  rephrase away a condition, or add information. The agent's ground truth is the
  Clause Inventory derived from the source file before any prompt is written.

intent: >
  A correct output satisfies all of these verifiable conditions:
  1. Every numbered clause in the source document appears in the summary.
  2. Multi-condition obligations preserve ALL their conditions (e.g. clause 5.2
     must name both Department Head and HR Director, not just "requires approval").
  3. The summary contains no information not present in the source document
     (no scope bleed such as "as is standard practice").
  4. Where a clause cannot be summarised without meaning loss, it is quoted
     verbatim and explicitly flagged.

context: >
  The agent may use only:
  - the input policy file (../data/policy-documents/policy_hr_leave.txt)
  - the Clause Inventory table in README.md, which is the ground truth for
    coverage checking
  The agent must NOT use any external knowledge about HR law, other municipal
  policies, or general practice. Any obligation wording not traceable to a
  numbered clause in the source is out of scope.

enforcement:
  - "Every numbered clause (1.1–8.2) must be represented in the summary output."
  - "Multi-condition obligations must preserve all conditions; dropping any
    condition (e.g. omitting one of the two LWP approvers) is a failed output."
  - "No sentence in the summary may assert a fact that cannot be traced to a
    numbered clause in the source document."
  - "If a clause resists faithful summary, refuse to paraphrase it: quote it
    verbatim with its clause number and flag it rather than guessing."
