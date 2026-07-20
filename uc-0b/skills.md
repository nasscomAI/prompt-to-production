skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content split into structured numbered sections.
    input: File path to a .txt policy document.
    output: A list of section objects, each with a section_heading and a list of clause objects (number, text).
    error_handling: Returns an error if the file does not exist, is not a .txt file, or is empty.

  - name: summarize_policy
    description: Takes structured sections (from retrieve_policy) and produces a compliant summary that preserves every numbered clause, all multi-condition obligations, and adds no external information.
    input: List of structured section objects with numbered clauses.
    output: A plain-text summary string. If a clause cannot be condensed without meaning loss, it is quoted verbatim and marked with [VERBATIM].
    error_handling: If any clause lacks a clear binding verb or condition, the clause is flagged for manual review rather than silently softened.
