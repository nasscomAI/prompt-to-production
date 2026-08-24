skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered sections,
      so that later stages operate on addressable clauses rather than on a wall of text.
    input: >
      path (str) — path to a policy .txt file whose clauses are numbered N.M at the
      start of a line, grouped under banner-delimited section headings.
    output: >
      dict with keys: title (list of header lines), sections (ordered list of
      {number, heading, clauses}), clauses (ordered list of {ref, text, section}),
      clause_count (int). Clause text is joined across continuation lines and
      whitespace-normalised, with no words added or removed.
    error_handling: >
      A missing file exits with an explicit path in the message. A file containing zero
      recognisable N.M clauses exits rather than returning an empty structure that a
      later stage would summarise into an empty file. A clause line that appears before
      any section heading is attached to a synthetic "0. PREAMBLE" section instead of
      being discarded.

  - name: summarize_policy
    description: >
      Turns structured sections into a compliant summary in which every clause is
      represented, every binding verb keeps its strength, and every meaning-critical
      clause is quoted verbatim and marked.
    input: >
      The dict returned by retrieve_policy.
    output: >
      A summary string organised by section, one entry per clause, each prefixed with
      its clause reference. Meaning-critical clauses are quoted verbatim and tagged
      [VERBATIM]; the remainder are compressed only by removing sentence-level filler.
      A COVERAGE AND VERIFICATION block at the end reports clause counts, verbatim
      counts, binding-verb counts and the result of the scope-bleed scan.
    error_handling: >
      A clause containing a number, deadline, amount, approver or absolute prohibition
      is never compressed — the compressor refuses and falls back to verbatim. If any
      clause would be unrepresented, or a banned scope-bleed phrase appears in the
      output, or a compressed line contains a token absent from its source clause, the
      run raises before the output file is written, so a defective summary is never
      produced on disk.
