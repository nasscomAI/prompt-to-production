# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy document and returns its content as structured
      numbered sections, preserving the source wording.
    input: >
      Path to a UTF-8 plain-text policy file (str).
    output: >
      Ordered collection of sections in the form (section_number, section_title,
      clauses) where each clause is (clause_number, clause_text).
    error_handling: >
      A missing, unreadable, or empty file is rejected with a descriptive error;
      lines that cannot be parsed into numbered clauses are reported rather than
      silently dropped.

  - name: summarize_policy
    description: >
      Produces a clause-complete policy summary that retains every numbered
      clause, its reference, and all binding conditions.
    input: >
      Structured policy sections from retrieve_policy.
    output: >
      A text summary that lists a clause group per section and every numbered
      clause within it, preserving conditions and binding language verbatim where
      a paraphrase could lose meaning.
    error_handling: >
      Verifies that all critical clauses are present (2.3, 2.4, 2.5, 2.6, 2.7,
      3.2, 3.4, 5.2, 5.3, 7.2) and refuses to emit a summary when any is missing;
      any clause too risky to compress is quoted verbatim and flagged.