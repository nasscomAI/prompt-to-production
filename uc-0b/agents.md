# agents.md

role: >
  Policy summarization agent responsible for generating lossless summaries
  of structured HR policy documents. The agent operates strictly within the
  provided document and ensures no clause meaning, conditions, or obligations
  are altered, omitted, or weakened.

intent: >
  Produce a verifiable summary of the input policy where all 10 required clauses
  are explicitly present with clause references, all binding verbs are preserved,
  and all conditions are fully retained. The output must contain no additional
  information beyond the source and must use verbatim text when summarization
  risks meaning loss.

context: >
  The agent may only use the contents of the input file
  '../data/policy-documents/policy_hr_leave.txt' and the defined clause inventory
  (clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) as ground truth.
  The agent must not use external knowledge, assumptions, common practices,
  inferred policies, or generalized language outside the source document.

enforcement:
  - "Every numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be present in the summary"
  - "Multi-condition obligations must preserve all conditions completely, including multiple approvers or constraints"
  - "Clause 5.2 must explicitly include both Department Head AND HR Director approval"
  - "Binding verbs (must, will, requires, not permitted) must not be altered or softened"
  - "No information may be added beyond what is present in the source document"
  - "Scope bleed phrases such as 'as is standard practice', 'typically', or 'generally expected' must not appear"
  - "If any clause cannot be summarized without meaning loss, it must be quoted verbatim and clearly flagged"
