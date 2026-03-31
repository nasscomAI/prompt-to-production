name: "retrieve_policy"
description: "Loads the HR leave policy text file and returns its contents as structured numbered sections."
input:
type: "string"
format: "file path to .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)"
output:
type: "object"
format: "JSON-like structure with numbered clauses as keys (e.g., '2.3', '2.4') and corresponding text as values"
error_handling:
"If the file path is invalid or file cannot be read, return an explicit error message indicating file access failure"
"If the document lacks clear numbered sections, return an error indicating unstructured input"
"If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing, flag missing clauses explicitly"
"If clause numbering is ambiguous or duplicated, return an error requesting clarification"
name: "summarize_policy"
description: "Generates a clause-complete summary from structured policy sections while preserving all obligations and conditions."
input:
type: "object"
format: "structured numbered sections with clause IDs as keys and full clause text as values"
output:
type: "string"
format: "plain text summary including all clause numbers and their obligations with preserved meaning"
error_handling:
"If any required clause is missing from input, return an error indicating incomplete clause coverage"
"If a clause contains multiple conditions, ensure all are preserved; otherwise flag as condition drop error"
"If summarization risks meaning loss, quote the clause verbatim and flag it"
"If output introduces information not present in input, reject and return scope bleed error"
"If binding verbs (must, requires, will, not permitted) are weakened or altered, return obligation softening error"
"If vague or generalized phrases appear (e.g., 'typically', 'generally'), reject output and flag scope bleed"
"If approval hierarchies or multi-actor requirements (e.g., both Department Head AND HR Director) are incomplete, return an explicit error"
