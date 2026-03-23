# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) of the .txt policy document.
    output: Structured data (e.g., dictionary or JSON) mapping clause numbers to their text.
    error_handling: If the file is missing or unreadable, return an error indicating the file could not be loaded.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with accurate clause references and preserved conditions.
    input: Structured numbered sections (data object).
    output: Formatted summary text block including all 10 clauses mapped exactly to their core obligations.
    error_handling: If a clause cannot be summarised without meaning loss, refuse to summarize it, quote it verbatim, and flag it.
