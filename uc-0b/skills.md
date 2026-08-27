skills:
  - name: retrieve_policy
    input: File path to the policy document (.txt).
    output: Structured content mapping each numbered clause exactly as it appears in the source text.
    error_handling: Raise an error if the file cannot be read or if no numbered clauses are found.

  - name: summarize_policy
    input: Structured policy content containing numbered clauses.
    output: A compliant summary retaining all clauses and multi-condition obligations.
    error_handling: Fails validation if any numbered clause from the input is omitted in the output. Raises an error if multi-condition obligations (e.g., dual approvers) are partially dropped or if unauthorized scope bleed is detected.
