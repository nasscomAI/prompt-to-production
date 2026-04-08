skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Structured representation of numbered sections and their corresponding text.
    error_handling: Return an explicit file not found error if the file doesn't exist. If section numbering is missing or ambiguous, return an error requesting a valid policy document format.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured policy sections (such as those outputted from retrieve_policy).
    output: A text summary containing clause references, preserving all conditions and numbered clauses.
    error_handling: If a clause cannot be summarized without the risk of meaning loss or scope bleed, return the clause verbatim and flag it.
