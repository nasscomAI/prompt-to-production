# skills.md

skills:

- name: retrieve_policy
  description: >
  Loads the policy text file and extracts structured numbered clauses.
  input: >
  File path to a .txt policy document
  output: >
  A list of clauses with identifiers (e.g., 2.3, 2.4) and corresponding text
  error_handling: >
  If file is missing or unreadable, raise an error.
  If clauses cannot be identified, return raw text with NEEDS_REVIEW flag.

- name: summarize_policy
  description: >
  Generates a clause-by-clause summary preserving all obligations, conditions,
  and binding language without omission or modification.
  input: >
  Structured list of clauses with identifiers and text
  output: >
  A formatted summary with each clause referenced and summarized or quoted
  error_handling: >
  If a clause cannot be summarized without losing meaning, output it verbatim
  and append [VERBATIM]. If ambiguity exists, flag NEEDS_REVIEW.
