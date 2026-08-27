skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document.
    output: Structured representation mapping clause numbers to text.
    error_handling: Return an explicit error flag if the file cannot be found, loaded, or parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured policy sections with clause numbers and text strings.
    output: A summarised text document strictly preserving every clause and condition.
    error_handling: Quote verbatim and flag if a clause cannot be summarized without meaning loss or condition dropping.
