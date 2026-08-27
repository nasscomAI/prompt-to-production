skills:
  - name: Document Reading
    description: Reads the policy document from the policy-documents directory and loads its content.
    input: File path (string) pointing to a policy text file.
    output: List of strings representing the lines of the document.
    error_handling: Returns an empty list and logs an error if the file cannot be found or opened.

  - name: Clause Extraction
    description: Identifies important clauses or meaningful statements from the policy document.
    input: List of strings representing the document lines.
    output: List of clauses (strings) that contain important policy rules.
    error_handling: Ignores empty or malformed lines and continues processing remaining text.

  - name: Summary Generation
    description: Generates a concise summary that preserves the meaning of the extracted clauses.
    input: List of extracted clauses.
    output: String containing the summarized policy text.
    error_handling: Produces a minimal summary and flags a warning if insufficient clauses are available.