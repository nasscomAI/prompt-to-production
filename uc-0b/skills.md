skills:
  - name: retrieve_policy
    description: Load the policy text document and extract numbered clauses.
    input: Policy document file path.
    output: List of clauses or structured text.
    error_handling: If file cannot be read, return NEEDS_REVIEW flag.

  - name: summarize_policy
    description: Produce a summary while preserving all policy obligations.
    input: Extracted clauses from the policy document.
    output: Summary text referencing the clauses.
    error_handling: If clause detection fails, return original text.