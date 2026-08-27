# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy file and return its content as structured
      numbered sections, preserving all clause numbers and text.
    input: >
      A file path (string) to a .txt policy document.
    output: >
      A list of dictionaries, each with keys: section_number (string),
      section_title (string), clauses (list of dicts with clause_number
      and clause_text).
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error
      with the file path. If the file has no recognizable section
      structure, return the entire text as a single section.

  - name: summarize_policy
    description: >
      Take structured policy sections and produce a compliant summary
      where every clause is represented with its original clause number,
      binding verbs are preserved, and multi-condition obligations
      retain all conditions.
    input: >
      A list of structured sections (output of retrieve_policy).
    output: >
      A string containing the full summary, organized by section,
      with each clause summarized on its own line prefixed by
      clause number. Verbatim-flagged clauses are marked with
      [VERBATIM — meaning loss risk].
    error_handling: >
      If a clause cannot be parsed or is empty, include it in the
      output with a note: "[EMPTY CLAUSE — check source document]".
      Never silently skip a clause.
