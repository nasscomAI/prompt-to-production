# skills.md

skills:
  - name: read_policy_document
    description: Reads a policy document text file.
    input: Path to policy text file.
    output: Full policy document as string text.
    error_handling: If file cannot be read, return an empty string and log an error.

  - name: summarize_policy
    description: Generates a concise summary while preserving all policy clauses.
    input: Full policy document text.
    output: A summarized version of the policy text.
    error_handling: If summarization fails, return the original document text.