# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and splits it into numbered sections and clauses, joining wrapped continuation lines.
    input: >
      path (string) to a plain-text policy file whose clauses start with "N.N" and whose
      section headings are "N. UPPERCASE HEADING".
    output: >
      (title_lines, sections) where sections is a list of
      {number, heading, clauses: [{id: "2.3", text: "..."}]} in source order.
    error_handling: >
      Missing file → exits with "Refusing: policy file not found". A file with no
      numbered clauses → exits with a refusal instead of summarising free text.
      Decorative divider lines are ignored; they never become clauses.

  - name: summarize_policy
    description: Condenses each clause with meaning-neutral rewrites and quotes it verbatim when condensing would drop a condition.
    input: >
      title_lines and sections as returned by retrieve_policy.
    output: >
      (summary_lines, report) — one summary line per clause formatted "[id] text", grouped
      under section headings, plus a report listing verbatim fallbacks, missing inventory
      clauses, missing required facts and any scope-bleed phrases found.
    error_handling: >
      For every clause, compares original vs condensed: any lost number, binding term
      (must, will, requires, only, regardless, under any circumstances, and/or, ...) or
      named role (Department Head, HR Director, Municipal Commissioner, ...) → the
      condensed text is discarded and the clause is quoted verbatim with [VERBATIM].
      Missing inventory clause or scope bleed → reported and the CLI exits non-zero.
