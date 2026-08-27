skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text and converts it into structured numbered clauses.
    input: A .txt policy path.
    output: An ordered list of clause IDs and clause text.
    error_handling: If no numbered clauses are found, raise a clear error instead of producing an incomplete summary.

  - name: summarize_policy
    description: Produces a clause-preserving summary from the structured clauses.
    input: An ordered list of clause IDs and clause text.
    output: A text summary where each line starts with the original clause number.
    error_handling: If a clause cannot be safely compressed, keep it verbatim rather than dropping conditions.
