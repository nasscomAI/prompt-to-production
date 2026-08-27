skills:

- name: retrieve_policy
  description: Loads a policy text file and returns its content organized into structured numbered sections and clauses.
  input:
  type: file_path
  format: "UTF-8 .txt policy document containing numbered sections and clauses"
  output:
  type: structured_sections
  format: "Ordered collection of numbered sections and clauses preserving original clause identifiers, numbering, and text"
  error_handling:
  invalid_input: "Return an error if the file path is missing, inaccessible, unreadable, or not a .txt file."
  malformed_document: "Return an error if numbered clauses cannot be reliably identified and structured."
  ambiguous_structure: "Preserve original text segments and flag sections requiring manual review rather than inferring numbering or hierarchy."
  failure_modes: "Do not omit, merge, rewrite, or reorder clauses during extraction."

- name: summarize_policy
  description: Produces a compliant policy summary from structured sections while preserving clause meaning and including clause references.
  input:
  type: structured_sections
  format: "Ordered collection of numbered policy clauses with original text and clause identifiers"
  output:
  type: summary_document
  format: "Clause-referenced summary covering every numbered clause, preserving all obligations, conditions, approvals, prohibitions, and scope"
  error_handling:
  invalid_input: "Return an error if structured sections are missing, empty, or lack clause identifiers."
  ambiguous_clause: "If a clause cannot be summarized without meaning loss, quote the clause verbatim and flag it for review."
  condition_loss_risk: "Preserve all conditions in multi-condition obligations; if preservation is uncertain, quote the clause verbatim and flag it."
  failure_modes: "Reject summaries that omit numbered clauses, soften binding obligations, drop approvers or conditions, introduce external information, or add unsupported policy interpretations."
