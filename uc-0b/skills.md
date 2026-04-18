# skills.md
skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns its contents parsed as structured numbered sections.
    input: Filepath to the raw .txt policy document (string).
    output: A structured format containing all numbered clauses extracted directly from the text.
    error_handling: Raise an IO error if the file is missing or unreadable. If text cannot be grouped into numbered sections, return an error indicating unsupported formatting.

  - name: summarize_policy
    description: Generates a fully compliant summary from the structured sections without softening obligations or dropping multi-conditions.
    input: Structured numbered sections extracted by retrieve_policy.
    output: A final compliant summary correctly incorporating all clauses, preserving constraints, and quoting verbatim when necessary.
    rules:
      - "Every numbered clause must be present in the summary"
      - "Multi-condition obligations must preserve ALL conditions — never drop one silently"
      - "Never add information not present in the source document"
      - "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
    error_handling: If a clause cannot be accurately summarized without altering the meaning, quote the clause exactly and flag it. Never guess or rely on external knowledge.
