# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content structured as numbered sections.
    input: Path to .txt file.
    output: Structured object of clauses.
    error_handling: Errors if file is missing or contains no numbered clauses.

  - name: summarize_policy
    description: Produces a compliant summary with clause references based on structured sections.
    input: Structured clause data.
    output: Summarized text with clause citations.
    error_handling: Flags skipped sections.

