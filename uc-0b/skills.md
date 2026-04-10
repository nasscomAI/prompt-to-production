skills:
  - name: retrieve_policy
    description: Loads policy text and extracts numbered clauses into structured sections.
    input: input_path string for a plain text policy document.
    output: Ordered mapping of clause_id to clause text.
    error_handling: Returns empty mapping when no numbered clauses can be parsed.

  - name: summarize_policy
    description: Produces clause-preserved summary lines with explicit clause numbers.
    input: Ordered mapping of clause_id to text.
    output: List of summary strings in clause order.
    error_handling: Raises validation error when clause mapping is empty.
