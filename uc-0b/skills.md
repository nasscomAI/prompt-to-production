# skills.md — UC-0B: Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) to a plain-text policy document.
    output: >
      A dictionary where each key is the clause number (e.g., "2.3", "5.2")
      and each value is the full text of that clause. Metadata fields
      (document title, version, effective date) are returned as top-level keys.
    error_handling: >
      If the file does not exist, raise FileNotFoundError with the path. If the
      file contains no parseable numbered sections, raise ValueError with a
      message indicating the document structure is unrecognisable. If a section
      cannot be parsed, log a warning and skip it — do not crash.

  - name: summarize_policy
    description: >
      Takes structured numbered sections and produces a compliant summary that
      preserves every clause, all conditions, and uses no external information.
    input: >
      A dictionary of numbered sections (output of retrieve_policy) and an
      optional list of clause numbers to focus on (if omitted, all clauses
      are summarised).
    output: >
      A plain-text summary with each clause referenced by number. Multi-condition
      obligations retain all conditions. Clauses that cannot be shortened are
      quoted verbatim and flagged.
    error_handling: >
      If a clause number from the input is not found in the structured sections,
      raise KeyError with the missing clause number. If the focused clause list
      is empty, return the full summary (no filtering applied).
