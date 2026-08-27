skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: File path as a string.
    output: Structured numbered sections.
    error_handling: Returns an error if the file is missing or unreadable.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections.
    output: A summary string retaining all clauses and conditions without scope bleed.
    error_handling: Quotes verbatim and flags if a clause cannot be summarized without meaning loss.
