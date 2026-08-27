# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      A file path to a .txt policy document.
    output: >
      A dictionary mapping section headers (e.g. "2. ANNUAL LEAVE") to a list
      of clause objects, each with clause_number (e.g. "2.3") and clause_text
      (the full text of that clause).
    error_handling: >
      If the file does not exist or cannot be read, raise an error with the
      file path. If no numbered clauses are found, warn that the document
      format may be unexpected.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary with clause references, preserving all conditions and obligations.
    input: >
      A dictionary of structured sections as returned by retrieve_policy.
    output: >
      A plain text summary organized by section headers, with each clause
      summarised as a bullet point prefixed by its clause number. All binding
      verbs and multi-condition obligations are preserved exactly.
    error_handling: >
      If a clause contains multiple conditions that risk being lost in
      summarisation, quote the clause verbatim and flag it with
      [VERBATIM — complex clause]. Never silently drop conditions.
