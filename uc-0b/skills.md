skills:

* name: "retrieve_policy"
  description: "Loads the HR leave policy from a .txt file and returns its contents as structured numbered sections without altering the source meaning."
  input:
  type: "file"
  format: "Plain-text (.txt) policy document, expected at ../data/policy-documents/policy_hr_leave.txt"
  output:
  type: "structured_data"
  format: "Ordered collection of numbered policy sections, where each section contains its clause number and exact source text"
  error_handling:
  invalid_input: "Reject the input if the file is missing, unreadable, empty, or not a plain-text policy document, and return a clear retrieval error without fabricating content."
  ambiguous_input: "Preserve ambiguous wording exactly as written and retain its clause number rather than interpreting or expanding it."
  clause_omission: "Verify that all numbered clauses found in the source are represented in the structured output; if any cannot be extracted reliably, flag the affected clause instead of silently omitting it."
  scope_bleed: "Do not add external knowledge, assumptions, standard practices, or explanatory content that is not present in the source document."
  obligation_softening: "Preserve binding verbs, conditions, exceptions, approvers, time limits, thresholds, and prohibitions exactly enough to prevent weakening or changing an obligation."

* name: "summarize_policy"
  description: "Takes structured policy sections and produces a compliant clause-referenced summary that preserves every obligation, condition, scope restriction, and prohibition."
  input:
  type: "structured_data"
  format: "Ordered numbered policy sections containing clause numbers and source text, as produced by retrieve_policy"
  output:
  type: "text"
  format: "Plain-text summary with explicit clause references for every numbered clause, preserving all material obligations and conditions"
  error_handling:
  invalid_input: "Reject input that lacks numbered sections, clause references, or source text, and do not generate a summary from incomplete or malformed data."
  ambiguous_input: "If a clause cannot be summarized without risking meaning loss, quote that clause verbatim and flag it as requiring verbatim preservation."
  clause_omission: "Check that every numbered clause is present in the final summary, including clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2; fail validation if any required clause is missing."
  scope_bleed: "Remove or reject any statement not supported by the source, including phrases such as 'as is standard practice', 'typically in government organisations', or 'employees are generally expected to' when those phrases are absent from the policy."
  obligation_softening: "Preserve binding force and all conditions, including deadlines, thresholds, exceptions, consequences, prohibitions, and required approvers; never replace a specific obligation with weaker or more general wording."
  multi_condition_obligations: "Preserve every condition in multi-condition clauses; specifically, clause 5.2 must state that Leave Without Pay requires approval from both the Department Head and the HR Director."
s
