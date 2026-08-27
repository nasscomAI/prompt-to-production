skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Content parsed into structured numbered sections.
    error_handling: Return an error if the file cannot be found, read, or if it is not a valid text file.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with explicit clause references.
    input: Structured numbered sections of the policy document.
    output: A compliant summary string preserving all conditions and referencing clauses.
    error_handling: If any clause cannot be summarized without losing meaning, quote it verbatim and explicitly flag it.
