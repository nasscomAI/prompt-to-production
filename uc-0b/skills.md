skills:

- name: retrieve_policy
  description: Loads a policy document and extracts structured clause-based content.
  input: Path to a .txt policy file.
  output: List or dictionary of numbered clauses with their full text.
  error_handling:
  If file is missing or unreadable, return empty structure and flag error.

- name: summarize_policy
  description: Generates a clause-preserving summary from structured policy sections.
  input: Structured clauses from retrieve_policy.
  output: A text summary including all clauses with preserved meaning.
  error_handling:
  If any clause is missing or ambiguous, include it verbatim instead of summarizing.
