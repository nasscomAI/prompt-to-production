# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Load a plain-text policy document from disk and return its content as a
      list of structured numbered sections, each with a section number and text.
    input: >
      file_path (string): absolute or relative path to a .txt policy document
      (e.g. policy_hr_leave.txt).
    output: >
      A list of dicts, each with keys: section_number (string, e.g. "2.3"),
      section_title (string, e.g. "Annual Leave"), and clause_text (string,
      the verbatim text of that clause). Clauses are returned in document order.
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error with the
      file path and stop — do not return partial or empty content. If a section
      cannot be parsed into a numbered clause (e.g. headers or blank lines),
      include it as a raw block with section_number set to null so downstream
      skills can detect and handle it explicitly.

  - name: summarize_policy
    description: >
      Take the structured clause list from retrieve_policy and produce a
      clause-complete, obligation-preserving summary of the policy document.
    input: >
      sections (list of dicts): the output of retrieve_policy — each dict has
      section_number, section_title, and clause_text.
    output: >
      A plain-text summary file (summary_hr_leave.txt) where every numbered
      clause is present, binding verbs are preserved exactly, multi-condition
      obligations are kept intact, and each summary point is tagged with its
      source clause number (e.g. "[2.3]"). Meaning-critical clauses (e.g. 5.2,
      7.2) are quoted verbatim and tagged with [VERBATIM — meaning-critical clause].
    error_handling: >
      If any of the 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4,
      5.2, 5.3, 7.2) is missing from the input sections, raise a warning
      listing the missing clause numbers and do not produce output — a partial
      summary is worse than no summary. If a clause text is present but too
      ambiguous to summarise without meaning loss, quote it verbatim and append
      [VERBATIM — meaning-critical clause] rather than paraphrasing.
