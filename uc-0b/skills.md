skills:
  - name: retrieve_policy
  description: Loads the HR policy text file and organizes it into structured numbered clauses for processing.
  input: Path to a .txt policy document.
  output: Structured policy content with numbered sections.
  error_handling: If the file is missing, unreadable, or malformed, report the error and stop processing without guessing.

  - name: summarize_policy
  description: Produces an accurate summary of the policy while preserving every clause, condition, and obligation.
  input: Structured policy sections.
  output: Summary with clause references and preserved conditions.
  error_handling: If a clause cannot be summarized without changing its meaning, include the original clause verbatim and flag it instead of making assumptions.
