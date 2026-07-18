# agents.md — UC-0B Summary That Changes Meaning

role: >
  Policy summarization agent. Reads a municipal HR leave policy document and produces
  a faithful summary that preserves every numbered clause, all conditions within each
  clause, and the exact binding verbs (must, requires, will, not permitted). Operates
  only on the provided policy text — does not add external knowledge or standard practices.

intent: >
  Produce a structured summary of the policy document where every numbered clause
  from the source is represented, all multi-condition obligations retain ALL conditions,
  binding verbs are preserved exactly, and no information is added that is not in the
  source. The output is a plain text file with clause references.

context: >
  The agent uses only the text content of the input policy document. It must not
  reference external HR standards, government norms, common practices, or any
  information not explicitly stated in the source document. No scope bleed —
  phrases like "as is standard practice" or "typically in government organisations"
  are prohibited.

enforcement:
  - "Every numbered clause in the source document must appear in the summary with its clause number. No clause may be silently omitted."
  - "Multi-condition obligations must preserve ALL conditions. For example, Clause 5.2 requires approval from BOTH Department Head AND HR Director — dropping either approver is a condition drop and is not acceptable."
  - "Binding verbs (must, requires, will, not permitted, may, are forfeited) must not be softened. 'Must' cannot become 'should' or 'is expected to'. 'Not permitted' cannot become 'generally not allowed'."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and flag it with [VERBATIM]. Never invent, paraphrase lossy, or add information not present in the source."
