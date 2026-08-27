skills:
  - name: retrieve_policy
    description: Reads and retrieves the HR policy document from the given file path.
    input: File path (string) pointing to a text file containing HR policy content.
    output: Raw policy text (string) exactly as read from the file.
    error_handling: Returns an error if the file path is invalid, file is missing, or content is empty.

  - name: summarize_policy
    description: Generates a concise summary of the HR policy while preserving all clauses, obligations, and conditions.
    input: Raw policy text (string).
    output: Summary text (string) that includes all clauses and conditions without altering meaning.
    error_handling: Refuses to summarize if input text is empty, unclear, or if summarization risks dropping clauses, conditions, or introducing new information.