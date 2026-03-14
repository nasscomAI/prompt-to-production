skills:
  - name: retrieve_policy
    description: Load the HR policy document and extract numbered clauses.
    input: Path to a .txt policy file.
    output: Structured list of clauses with clause numbers and text.
    error_handling: If file cannot be read or format is invalid, return an error and stop processing.

  - name: summarize_policy
    description: Generate a compliant summary preserving clause references and conditions.
    input: Structured policy clauses.
    output: Text summary referencing each clause.
    error_handling: If a clause cannot be summarized without losing meaning, quote the clause verbatim and mark it for review.