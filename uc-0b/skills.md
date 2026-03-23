- name: retrieve_policy
  description: Loads the HR policy text file and converts it into structured numbered sections.
  input:
  type: file path
  format: .txt
  output:
  type: structured data
  format: list of numbered clauses with text
  error_handling: >
  If the file is missing, unreadable, or not in expected format, return an error message
  and stop execution.

- name: summarize_policy
  description: Generates a compliant summary from structured policy clauses while preserving all obligations.
  input:
  type: structured data
  format: list of numbered clauses
  output:
  type: text
  format: summarized policy with clause references
  error_handling: >
  If clauses are missing, ambiguous, or any condition cannot be preserved, the system must
  flag the issue or quote the clause verbatim instead of summarizing incorrectly.
