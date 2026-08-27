skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: File path to the .txt policy document.
    output: Structured document content divided into numbered sections/clauses.
    error_handling: Raises an error if the file is not found or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured document content with numbered sections/clauses.
    output: A comprehensive summary referencing every clause without losing conditions.
    error_handling: Fails and flags the clause verbatim if it cannot be summarized without altering its meaning or dropping conditions.
