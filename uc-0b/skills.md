* name: retrieve_policy
  description: Loads a policy .txt file and converts it into structured numbered sections for downstream processing.
  input:
  type: string
  format: file path to a .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)
  output:
  type: object
  format: structured representation of the document as numbered clauses and sub-clauses (e.g., { "2.3": "...", "2.4": "...", ... })
  error_handling:

  * If the file path is invalid or file cannot be read, return an explicit error indicating file access failure.
  * If the document is unstructured or missing clause numbering, return an error indicating inability to map structured sections.
  * If any of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing or not identifiable, flag as incomplete retrieval.

* name: summarize_policy
  description: Generates a compliant summary of the policy document from structured clauses while preserving all obligations and conditions.
  input:
  type: object
  format: structured numbered clauses (e.g., { "2.3": "...", "2.4": "...", ... })
  output:
  type: string
  format: structured summary text with explicit clause references and preserved conditions for each clause
  error_handling:

  * If any required clause is missing from input, return an error indicating clause omission.
  * If a clause contains multiple conditions and any condition cannot be preserved, halt and return an error indicating condition loss risk.
  * If summarization introduces external assumptions or phrases not present in the source (scope bleed), reject output and return an error.
  * If a clause cannot be summarized without altering meaning, include the verbatim clause and flag it explicitly.
