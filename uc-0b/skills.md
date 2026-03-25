skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) to the .txt policy document.
    output: Structured representation (e.g., JSON or dictionary) containing the numbered clauses and their corresponding text.
    error_handling: Return an explicit error if the file cannot be found or read, requesting a valid file path.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Structured policy sections (output from retrieve_policy).
    output: A string containing the compliant summary that explicitly references all clause numbers.
    error_handling: Return a validation error if the provided sections are incomplete or malformed.
