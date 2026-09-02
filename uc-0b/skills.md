skills:
  - name: retrieve_policy
    description: >
      Loads a policy .txt file and returns its content as structured numbered
      sections, preserving the original wording of every clause.
    input: >
      policy_path (str) — path to a .txt policy document whose clauses are
      numbered in N.M form at the start of a line.
    output: >
      tuple (clauses, header, raw_source). clauses is a list of dicts in source
      order, each with section (str, e.g. "2"),
      section_title (str), clause (str, e.g. "2.3") and text (str — the clause
      wording with wrapped lines rejoined and nothing else altered), plus the
      document header lines preceding the first numbered clause.
    error_handling: >
      A missing or unreadable file exits with the path named, before anything is
      written. A file containing no N.M clause numbers exits rather than
      returning an empty structure, because a silently empty parse would satisfy
      a completeness check vacuously and produce a summary of nothing. Lines
      before the first numbered clause are retained as header, not discarded.

  - name: summarize_policy
    description: >
      Renders the structured clauses as a clause-referenced summary in which
      binding clauses are reproduced verbatim and marked, and no wording is
      introduced that is absent from the source.
    input: >
      sections (list of dicts from retrieve_policy); header (list of str);
      output_path (str); raw_source (str) — the unparsed policy text, used for
      verification independent of the parse.
    output: >
      A .txt summary at output_path, grouped by section, every clause present
      under its own number, binding clauses carrying a [VERBATIM] marker, and an
      index of multi-condition obligations. Returns counts of clauses written,
      clauses quoted verbatim and clauses condensed.
    error_handling: >
      Before writing, asserts that every clause number found in raw_source
      appears both in the parse and in the rendered text, that every condition
      token in a binding clause survives, and that no scope-bleed phrase has
      entered. Clause numbers are taken from the raw source rather than from
      sections, because sections and the rendered text come from the same parse
      and comparing them cannot detect a clause the parser never saw. If any check fails it prints
      each offending clause and exits without writing, so a lossy summary is
      never produced. A clause it cannot condense safely is emitted verbatim,
      never dropped and never paraphrased, and it never invents a clause the
      source does not contain.
