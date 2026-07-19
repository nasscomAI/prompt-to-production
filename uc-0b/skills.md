skills:
  - name: retrieve_policy
    description: Load a policy text file and return the raw content structured by sections and numbered clauses.
    input: File path of the policy document (.txt format).
    output: List of dictionaries containing clause numbers and their raw text.
    error_handling: Raise FileNotFoundError if the file path is invalid or inaccessible.

  - name: summarize_policy
    description: Summarize the structured clauses while strictly preserving all conditions, obligations, and reference numbers.
    input: List of structured clauses from retrieve_policy.
    output: Markdown formatted text document containing the clause summaries.
    error_handling: Fall back to verbatim quotes if a clause is too complex or ambiguous to summarize safely.
