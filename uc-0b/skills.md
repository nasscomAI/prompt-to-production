# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections.
    input: Path to a policy .txt file.
    output: A dict mapping section/clause numbers (e.g. "2.4") to their verbatim text.
    error_handling: >
      If the file is missing or unreadable, raises a clear FileNotFoundError with the
      path. If a referenced clause number is not found, returns an empty string for
      that key rather than inventing text.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that preserves every clause and condition with references.
    input: The structured sections dict from retrieve_policy.
    output: A plain-text summary string with one entry per clause, each citing its clause number and binding verb.
    error_handling: >
      If a clause cannot be condensed faithfully, emits the source verbatim wrapped in
      [VERBATIM] ... [END VERBATIM] and continues with the remaining clauses instead
      of omitting it.
