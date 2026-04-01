name: retrieve_policy
description: "Loads a .txt HR policy document and returns its contents as structured numbered clauses."
input:
type: "string"
format: "File path to a .txt document (e.g., ../data/policy-documents/policy_hr_leave.txt)"
output:
type: "object"
format: "Dictionary or JSON with clause numbers as keys and corresponding clause text as values, preserving original wording"
error_handling:
"If file path is invalid or file cannot be read, return an explicit file access error"
"If document lacks clear numbered clauses, return a structured parsing error and do not infer or fabricate structure"
"If clauses are ambiguous or partially missing, return an error indicating incomplete source data"
"Do not modify, summarize, or interpret content; return raw structured text only"
name: summarize_policy
description: "Generates a clause-complete, meaning-preserving summary from structured policy clauses with explicit references."
input:
type: "object"
format: "Structured clauses as dictionary/JSON with clause numbers (e.g., 2.3, 2.4, etc.) mapped to full text"
output:
type: "string"
format: "Plain text summary including all required clause numbers with preserved obligations, conditions, and binding verbs"
error_handling:
"If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing, return an error and do not produce summary"
"If multi-condition obligations are detected but any condition is lost or unclear, return an error indicating condition drop risk"
"If output introduces information not present in input (scope bleed), reject and return an error"
"If binding verbs are altered or softened, return an obligation integrity error"
"If a clause cannot be summarized without meaning loss, include it verbatim and flag it; if not possible, return an error"
"If input structure is malformed or ambiguous, return a validation error and halt processing"