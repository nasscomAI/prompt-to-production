# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document (string).
    output: A list of sections, each containing the section heading and its numbered clauses with full text preserved.
    error_handling: If the file is missing or unreadable, exit with a clear error message. If the file has no recognizable clause structure, return the raw text with a warning.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves every clause, all conditions, and binding verbs with clause references.
    input: Structured sections from retrieve_policy (list of section headings and their numbered clauses).
    output: A plain text summary file where each clause is summarized with its clause number, all multi-condition obligations retain every condition, and binding verbs are preserved exactly. Clauses that cannot be summarized without meaning loss are quoted verbatim and flagged with [VERBATIM].
    error_handling: If a clause is ambiguous or cannot be faithfully condensed, quote it verbatim rather than risk meaning loss. Never add information not present in the source.
