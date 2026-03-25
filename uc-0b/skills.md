skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path string pointing to the .txt policy document.
    output: Structured numbered sections mapping clause numbers to text.
    error_handling: Refuse to proceed and return a file read error if the document is missing, inaccessible, or invalid.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections containing the policy clauses.
    output: A compliant text summary explicitly referencing the numbered clauses.
    error_handling: Return a validation error if any provided sections are empty or if the input is malformed, to prevent missing clauses in the summary.
