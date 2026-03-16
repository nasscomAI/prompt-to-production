skills:

- name: retrieve_policy
  description: Loads a policy text file and extracts numbered clauses as structured sections.
  input: Path to a policy text file (.txt) containing numbered clauses.
  output: A list of structured clauses where each element contains clause number and clause text.
  error_handling: If the file cannot be read or is empty, the function raises a readable error and stops execution.
- name: summarize_policy
  description: Produces a structured summary from policy clauses while preserving obligations and conditions.
  input: A list of structured policy clauses containing clause number and text.
  output: A summarized text document where each clause is summarized or quoted while preserving meaning.
  error_handling: If a clause is ambiguous or cannot be safely summarized, the clause is quoted verbatim and marked for careful review.
