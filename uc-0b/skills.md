# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as
      structured numbered sections ready for summarisation.
    input: Path string to a policy .txt file whose clauses are numbered
      `N.N` at line start with indented continuation lines.
    output: Ordered list of dicts {number, text, section} where `number`
      is the clause id (e.g. "5.2"), `text` is the whitespace-normalised
      clause text, and `section` is the enclosing heading (e.g.
      "5. LEAVE WITHOUT PAY (LWP)").
    error_handling: File missing/unreadable exits cleanly with ERROR on
      stderr and exit code 1 (no traceback); a file with no numbered clauses
      exits with a clear "not a policy document" error rather than producing
      an empty summary.

  - name: summarize_policy
    description: Produces a compliant summary from structured sections with a
      clause reference for every clause.
    input: The ordered list of {number, text, section} dicts returned by
      retrieve_policy.
    output: Summary text containing every clause quoted verbatim under its
      section heading, plus a CLAUSE INVENTORY CHECK verifying the 10
      ground-truth clauses (2.3–7.2) are PRESENT/MISSING.
    error_handling: If any required ground-truth clause is absent from the
      input sections, the output carries an explicit WARNING naming the
      missing clause(s) instead of failing silently; empty input list yields
      a summary marked as having zero coverage rather than crashing.
