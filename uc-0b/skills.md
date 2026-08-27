skills:
  - name: retrieve_policy
    description: Loads the specified text policy file and parses it into structured numbered sections for processing.
    input: Path to the .txt policy file.
    output: A structured object or list of sections with clause numbers and text.
    error_handling: Returns an error if the file is missing, unreadable, or contains no identifiable numbered clauses.

  - name: summarize_policy
    description: Processes structured policy sections into a compliant summary that preserves all obligations and conditions.
    input: Structured policy sections (from retrieve_policy).
    output: A formatted summary string with clause references.
    error_handling: Flags sections that are too ambiguous or complex for summarization for verbatim inclusion.
