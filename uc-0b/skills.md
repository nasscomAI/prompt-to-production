# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file, returns content as structured numbered sections.
    input: File path to the .txt policy document (string)
    output: Structured document content organized by numbered sections (JSON array or object)
    error_handling: If the file is missing or cannot be read, return an error indicating the file is inaccessible.

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references.
    input: Structured policy sections (JSON array or object)
    output: Compliant summary text containing accurate references to specific clauses (string)
    error_handling: If the input sections are empty or malformed, return an error requesting valid structured sections.
