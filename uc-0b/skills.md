skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections
    input: File path string to the policy document
    output: Structured representation (e.g. dictionary or list) of numbered sections
    error_handling: Raise error on file read failure or if content cannot be structurised.

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references
    input: Structured sections from retrieve_policy
    output: A precise summary string containing all clauses and preserving all conditions
    error_handling: Output "Error: Clause omission detected" if unable to faithfully preserve constraints.
