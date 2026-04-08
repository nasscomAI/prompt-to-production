- name: retrieve_policy
  description: Loads policy text file and extracts structured numbered clauses.
  input:
    type: text file
    format: policy document with numbered sections
  output:
    type: list
    format: [{clause_number, clause_text}]
  error_handling: >
    If file cannot be read, raise error.
    If no clauses detected, return error.

- name: summarize_policy
  description: Produces a compliant summary preserving all clauses and conditions.
  input:
    type: structured clauses
    format: list of clause_number and text
  output:
    type: text
    format: summarized clauses with references
  error_handling: >
    If any clause is missing in output, raise error.
    If meaning loss risk detected, quote clause verbatim and flag it.