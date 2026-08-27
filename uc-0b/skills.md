skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts content as structured, numbered sections to ensure no clauses are missed.
    input: File path (string) to the source policy document.
    output: List of objects containing 'clause_id' (string) and 'content' (string).
    error_handling: Raise error if file is inaccessible or if numbering structure is missing.

  - name: summarize_policy
    description: Produces a high-fidelity summary of policy sections, preserving all multi-condition obligations and cross-referencing original clause numbers.
    input: List of structured objects from retrieve_policy.
    output: Markdown-formatted summary text with explicit clause numbering and condition preservation.
    error_handling: If a clause is ambiguous or too complex for safe summarization, the skill must return the verbatim text flagged for manual review.
