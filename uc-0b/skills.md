- name: retrieve_policy
  description: Loads a policy text file and extracts structured numbered clauses.
  input: file path to .txt policy document
  output: list of clauses with clause number and text
  error_handling: >
    If the file is missing or unreadable, return an error. If clauses cannot be
    identified, return empty list and flag parsing issue.

- name: summarize_policy
  description: Generates a compliant summary preserving all clauses and their conditions.
  input: structured list of policy clauses
  output: summarized text with clause references
  error_handling: >
    If any clause is missing, incomplete, or conditions are dropped, reject the summary.
    If summarisation risks meaning loss, include the original clause verbatim and flag it.
