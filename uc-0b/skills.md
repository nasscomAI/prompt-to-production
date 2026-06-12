name: retrieve_policy
description: Load a policy text file and convert it into structured numbered clauses without altering content.
input:
type: string
format: file path to .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)
output:
type: structured data
format: ordered list or map of numbered clauses (e.g., 2.3, 2.4, ...) preserving original text verbatim
error_handling: >
If the file is missing, unreadable, or malformed, return a structured error indicating input failure.
If clause numbering cannot be reliably extracted, refuse to proceed rather than guessing.
Do not modify, interpret, or infer missing clauses; return only what is explicitly present.


name: summarize_policy
description: Generate a compliant summary from structured policy clauses while preserving meaning, conditions, and clause references.
input:
type: structured data
format: ordered numbered clauses with original text content
output:
type: string
format: summary text with explicit clause references and preserved obligations
error_handling: >
If any required clause is missing, refuse to generate the summary.
If a clause contains multiple conditions and they cannot all be preserved, output the clause verbatim and flag it.
If input is ambiguous or incomplete, do not infer or add information; return an error.
If output would introduce scope bleed, soften obligations, or omit conditions, halt and return a failure indicating violation of constraints.

