skills:
  - name: retrieve_policy
    description: Loads the policy text file and extracts numbered clauses as structured sections.
    input: Path to a policy text file.
    output: List of clauses with clause number and clause text.
    error_handling: If the file cannot be read, return an empty list and report the error.

  - name: summarize_policy
    description: Produces a compliant summary from structured clauses while preserving obligations and conditions.
    input: List of structured policy clauses.
    output: A summary text containing all clauses.
    error_handling: If a clause cannot be safely summarized, include the original clause verbatim.