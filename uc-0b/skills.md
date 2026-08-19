# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections and clauses.
    input: >
      input_path (str) to a plain-text policy document whose clauses are
      numbered in N.N form (e.g. 2.3) under section headers of the form
      "N. TITLE".
    output: >
      An ordered structure of sections, each with its number, title, and the
      list of clauses under it; every clause has its reference (e.g. "5.2") and
      its full text with internal whitespace normalised.
    error_handling: >
      If the file is missing or contains no numbered clauses, it raises a clear
      error before any summary is produced (never emits an empty or partial
      summary silently). Lines that are not clauses (borders, blank lines) are
      ignored, not misparsed as clauses.

  - name: summarize_policy
    description: Turns structured sections into a clause-referenced summary that preserves every clause and all conditions.
    input: The structured sections returned by retrieve_policy.
    output: >
      A text summary listing every section and, under it, every clause tagged
      with its reference, its binding verb where present, and a MULTI-CONDITION
      marker where a clause carries more than one required condition. Ends with
      a clause-inventory line for verification.
    error_handling: >
      If a clause would lose a condition or its binding force under compression,
      it is emitted verbatim and marked [VERBATIM] instead. The final inventory
      count is checked against the parsed clause count; a mismatch aborts with
      an error rather than writing an incomplete summary.
