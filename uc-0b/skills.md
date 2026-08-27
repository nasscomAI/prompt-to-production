# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: A file path (string) pointing to a .txt policy document.
    output: A dictionary keyed by section number (e.g. "1", "2.3") with the clause text as the value. Returns the full document content grouped by numbered clause.
    error_handling: If the file path is missing or the file does not exist, return an error message: "Error: Input file not found at [path]." If the file is empty, return: "Error: Input file is empty."

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: A dictionary of numbered sections (from retrieve_policy) with clause text.
    output: A plain-text summary that contains every clause number, preserves all conditions within multi-part obligations, and flags any clause requiring verbatim inclusion with [VERBATIM].
    error_handling: If any clause is missing from the source sections, flag it and do not invent content. If a clause contains multiple conditions and summary would drop one, quote it verbatim and append [VERBATIM — meaning cannot be preserved in summary].
