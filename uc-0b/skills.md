skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and extracts numbered clauses.
    input: Path to policy text file (.txt).
    output: List of numbered policy clauses.
    error_handling: If a clause cannot be parsed correctly, mark it for review.

  - name: summarize_policy
    description: Produces a compliant summary preserving clause numbers and obligations.
    input: List of numbered clauses from the policy document.
    output: Structured summary text referencing each clause.
    error_handling: If summarizing would remove conditions or meaning, quote the clause verbatim and flag it.