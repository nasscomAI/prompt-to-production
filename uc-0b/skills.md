skills:
  - name: retrieve_policy
    description: Loads the .txt HR policy file and returns the content organised as structured numbered sections.
    input: string (File path to the .txt policy document)
    output: JSON list of objects (containing section number and raw text)
    error_handling: If the file is not found or cannot be parsed into numbered sections, throw an error indicating that manual review is required.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses, conditions, and explicit clause references.
    input: JSON list of objects (structured sections from retrieve_policy)
    output: string (Formatted markdown summary with explicit clause references)
    error_handling: If a structured section lacks a clear requirement or is ambiguous to summarize without meaning loss, quote the section verbatim and flag it in the output instead of guessing.
