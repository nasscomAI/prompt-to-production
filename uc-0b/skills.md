# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads a policy document and returns its numbered clauses as structured
      sections.
    input: Path to a plain-text policy file (e.g. policy_hr_leave.txt).
    output: A list of (clause_number, clause_text) tuples, one per numbered
      clause such as 2.3, 5.2, in document order, with whitespace normalised.
    error_handling: If no numbered clauses are found or the file cannot be
      read, raise an error and produce no output rather than writing an empty
      or partial summary.

  - name: summarize_policy
    description: >
      Takes the structured sections and produces a compliant summary that
      preserves every clause and every condition.
    input: The list of (clause_number, clause_text) tuples from retrieve_policy.
    output: A summary text where every numbered clause appears, conditions are
      preserved in full, and no text is added beyond the source.
    error_handling: Any clause that cannot be condensed without losing meaning
      is quoted verbatim and flagged [VERBATIM]. After building, verify the
      critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are
      all present, and verify 5.2 still names both the Department Head and the
      HR Director; fail loudly if any check does not pass.
