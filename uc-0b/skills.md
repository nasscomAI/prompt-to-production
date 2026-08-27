skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (String).
    output: Document content as structured numbered sections (List of corresponding sections/clauses).
    error_handling: Return an explicit error if the file is not found, cannot be read, or if valid numbered clauses cannot be identified.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured sections of the policy document (List of corresponding sections/clauses).
    output: A precise summary text preserving all clauses and multi-condition obligations.
    error_handling: Quote verbatim and flag if a clause is ambiguous or cannot be summarized without potentially losing meaning or dropping conditions.
