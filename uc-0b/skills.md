skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and returns its contents as structured numbered clauses.
    input: Path to a .txt policy document.
    output: Structured list of numbered policy clauses.
    error_handling: If the file cannot be read or clauses cannot be detected, return NEEDS_REVIEW.

  - name: summarize_policy
    description: Produces a compliant summary of the policy document while preserving all clause obligations.
    input: Structured list of numbered policy clauses.
    output: Summary text referencing the clauses.
    error_handling: If summarization risks losing meaning, quote the clause verbatim and flag it.
