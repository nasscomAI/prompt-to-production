skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Structured content mapping policy sections and their numbered clauses.
    error_handling: Return error if file is missing, unreadable, or not a valid text document.

  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a compliant summary with clause references.
    input: Structured content containing numbered policy sections.
    output: A functional summary string ensuring all original clauses and conditions are preserved without meaning loss.
    error_handling: If any clause cannot be accurately summarized without losing meaning or condition, quote it verbatim and flag it.
