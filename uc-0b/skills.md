skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections and clauses.
    input: Path to a plain-text policy document whose clauses follow the N.N numbering pattern.
    output: >
      An ordered structure of sections (title + section number) each containing its
      clauses, where every clause carries its exact clause number and full text with
      internal line breaks normalised to single spaces.
    error_handling: >
      If the file is missing or unreadable, raise a clear error and do not continue.
      If a section contains no numbered clauses, it is retained as metadata but marked
      as having no binding clauses so it cannot be mistaken for a dropped clause.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that preserves every clause, its number, and all its conditions.
    input: The structured sections/clauses produced by retrieve_policy.
    output: >
      A text summary grouped by section, one line per clause, each prefixed with its
      clause number, preserving all binding verbs and all conditions; multi-condition
      clauses are marked [MULTI-CONDITION] and any clause kept verbatim is marked
      [VERBATIM]. Ends with a completeness check line listing total clauses covered.
    error_handling: >
      Never invents or omits a clause. If any source clause is missing from the
      generated summary, the skill refuses to emit the summary and instead reports the
      missing clause numbers. It does not soften binding verbs and does not add text
      that is absent from the source.
