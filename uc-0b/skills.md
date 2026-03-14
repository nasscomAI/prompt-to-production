# skills.md

skills:
  - name: summarize_policy_document
    description: Reads a policy document file and generates a summary that includes all numbered clauses with their core obligations and binding verbs preserved.
    input: A file path (string) to the policy document text file.
    output: A string containing the summary text of the policy.
    error_handling: If the file does not exist or cannot be read, raise a FileNotFoundError; if the document is incomplete (missing clauses), output an error message indicating missing information instead of guessing.
