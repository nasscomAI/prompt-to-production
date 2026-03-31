# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy file and return its content as structured numbered
      sections with clause identifiers preserved.
    input: >
      A file path (string) pointing to a .txt policy document.
    output: >
      A list of sections, each containing: section_number (e.g. "2.3"),
      section_heading (e.g. "ANNUAL LEAVE"), and section_text (the full
      text of that clause). The numbered hierarchy (1.x, 2.x, etc.) must
      be preserved exactly as in the source.
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error
      with the file path. If the file contains no recognisable numbered
      clauses, return the raw text and flag it as unstructured.

  - name: summarize_policy
    description: >
      Take structured policy sections and produce a clause-by-clause
      compliant summary that preserves all obligations and conditions.
    input: >
      A list of structured sections as returned by retrieve_policy.
    output: >
      A plain-text summary file where each line references a clause
      number (e.g. §2.3) and summarises it. All 10 critical clauses
      (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be
      present. Binding verbs must match the source strength. Multi-
      condition clauses must list all conditions. Any clause that
      cannot be summarised without meaning loss is quoted verbatim
      with a [VERBATIM] flag.
    error_handling: >
      If a section has no identifiable obligation or condition, include
      it in the summary with a note: [INFO-ONLY: no binding obligation].
      Never silently skip a clause.
