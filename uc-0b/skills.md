skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) pointing to the .txt policy document.
    output: Structured text containing clearly separated and numbered sections/clauses.
    error_handling: Return an error if the file is missing, unreadable, or not structured with clear numbered clauses.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, ensuring no meaning loss or dropped conditions.
    input: Structured numbered sections of the policy document.
    output: A summary text document containing all original clauses and preserving all multi-condition obligations.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it. Refuse to add external information if the document is ambiguous.
