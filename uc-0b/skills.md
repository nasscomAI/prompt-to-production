# skills.md
skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns structured numbered clauses.
    input: Path to a .txt policy document with numbered sections and wrapped lines.
    output: Ordered list of clause objects with clause number and normalized clause text.
    error_handling: If file is missing, unreadable, or has no numbered clauses, stop with a clear error and do not produce a partial summary.

  - name: summarize_policy
    description: Produces a clause-preserving summary from structured clauses with references.
    input: Ordered clause list from retrieve_policy.
    output: Summary text that includes every numbered clause, preserves multi-condition obligations, and marks verbatim clauses when shortening risks meaning loss.
    error_handling: If required clauses are missing or clause text is ambiguous after parsing, fail fast and report which clause cannot be summarized safely.
