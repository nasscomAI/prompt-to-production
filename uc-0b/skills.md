skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text and splits it into numbered clauses.
    input: Path to policy .txt file.
    output: List of numbered policy clauses.
    error_handling: If a clause cannot be parsed, mark it as NEEDS_REVIEW.

  - name: summarize_policy
    description: Produces a structured summary preserving clause numbers and obligations.
    input: List of numbered policy clauses.
    output: Text summary referencing each clause.
    error_handling: If summarization risks meaning loss, quote the clause verbatim and flag it.