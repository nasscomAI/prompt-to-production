# skills.md — UC-0B

skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections to preserve strict references.
    input: File path to the policy .txt file.
    output: Dictionary mapping section/clause numbers to their text content.
    error_handling: Raises an exception if the file cannot be read or parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary preserving all required clauses and conditions.
    input: Dictionary of structured clauses.
    output: String representing the final summary text with clause references.
    error_handling: Verbatim quotes the clause if summarization drops key verbs or conditions.
