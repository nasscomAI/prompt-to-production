skills:
  - name: retrieve_policy
    description: Loads an HR policy text file and parses it into structured numbered sections and clauses with metadata.
    input: File path to policy document (str).
    output: Dictionary mapping section headings and clause numbers to raw clause text (dict).
    error_handling: Raises FileNotFoundError if the file path is invalid or unreadable.

  - name: summarize_policy
    description: Transforms structured policy clauses into an exhaustive, obligation-faithful summary retaining all binding verbs, conditions, and clause citations.
    input: Structured policy dictionary (dict).
    output: Formatted summary text string organized by sections with clause citations (str).
    error_handling: Flags and outputs verbatim any complex multi-condition clause where semantic compression risks altering legal meaning or obligations.
