skills:
  - name: retrieve_policy
    description: Reads text policy document and parses all numbered sections and clauses into structured items.
    input: File path to policy document (.txt)
    output: Structured dict/list of clauses with section numbers, titles, and text contents.
    error_handling: Raises FileNotFoundError if file is missing.

  - name: summarize_policy
    description: Processes parsed clauses and generates a strict, complete, non-softened summary preserving all conditions.
    input: Structured policy sections
    output: Formatted text summary string containing every numbered clause with exact binding rules.
    error_handling: Flags any clause that cannot be summarized without loss of meaning and includes quote verbatim.
