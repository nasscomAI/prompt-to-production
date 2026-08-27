# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured, numbered sections and clauses (the ground-truth inventory the summary is built from).
    input: >
      input_path (path to policy_hr_leave.txt). Plain UTF-8 text using
      "N. TITLE" section headers and "N.M clause text" clause lines, with
      indented continuation lines.
    output: >
      A structured object: an ordered list of sections, each
      {number, title, clauses:[{number, text}]}, plus a flat {clause_number: text}
      index for lookup. Continuation lines are joined and whitespace collapsed so
      each clause is one clean string. No clause text is altered, dropped, or added.
    error_handling: >
      If the file is missing or unreadable, fail loudly (raise) — an empty or
      partial inventory must never be summarised silently. Lines that match no
      section/clause pattern are ignored as decoration (dividers, banner). If a
      required tracked clause is absent from the parse, record it as MISSING so
      summarize_policy can flag it rather than emit an incomplete summary quietly.

  - name: summarize_policy
    description: Takes the structured sections and produces a clause-referenced summary that preserves every clause, all conditions, and each binding verb — with no information not present in the source.
    input: >
      The structured sections object from retrieve_policy, plus output_path
      (path to summary_hr_leave.txt).
    output: >
      A summary written to output_path. Every numbered clause appears tagged with
      its clause number. The 10 high-risk clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2,
      3.4, 5.2, 5.3, 7.2) are emitted verbatim and marked [BINDING] so their
      conditions and verb strength (must / requires / will / not permitted) cannot
      be softened. A COMPLETENESS CHECK footer lists every tracked clause and
      confirms it is present; clause 5.2 is additionally checked for BOTH the
      Department Head and the HR Director.
    error_handling: >
      If any tracked clause is missing from the input, do NOT produce a
      "clean" summary — emit the clause line as [MISSING — FLAG FOR REVIEW] and
      mark the run as failed in the footer. If clause 5.2 loses either approver,
      flag it as a dropped condition. Never paraphrase a binding clause into a
      weaker verb; when meaning cannot survive condensation, quote verbatim.
      Never insert phrases not traceable to a source clause (no "as is standard
      practice", "typically in government organisations", "generally expected to").
