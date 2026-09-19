skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as numbered sections and clauses.
    input: path (str) to a .txt policy file.
    output: List of sections, each with number, title and a list of (clause_id, full clause text).
    error_handling: Unreadable file or no numbered clauses found stops with a clear error message.

  - name: summarize_policy
    description: Turns structured sections into a summary that keeps every clause and its conditions.
    input: List of sections from retrieve_policy.
    output: Plain text summary with clause references.
    error_handling: If a clause has no approved summary, or a required term (binding verb, number, approver) is missing from it, the clause is quoted verbatim and marked NEEDS REVIEW.