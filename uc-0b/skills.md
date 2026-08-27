skills:
  - name: retrieve_policy
    description: Loads a policy file (.txt) and returns its content as structured, numbered sections.
    input: File path (string)
    output: Structured JSON or list of sections with clause numbers and text.
    error_handling: Raise an error if the file is not found, not a .txt file, or has no numbered clauses.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary preserving all conditions and clause references.
    input: Structured policy sections (JSON/List)
    output: Formatted summary (text) with all conditions intact.
    error_handling: Refuse to summarize if a clause is ambiguous and cannot be quoted verbatim.
