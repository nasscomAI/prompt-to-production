skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts the content, organizing it by sections and numbered clauses.
    input: File path of the policy document.
    output: String representing the policy content or a structured mapping of sections.
    error_handling: Raises an error if the file is not found or cannot be read.

  - name: summarize_policy
    description: Generates a summary that preserves all core obligations and conditions, referencing each clause exactly.
    input: Structured sections or raw content of the policy.
    output: A precise text summary containing references to all required clauses.
    error_handling: Quotes the clause verbatim if a concise summary would lose critical conditions or obligations.
