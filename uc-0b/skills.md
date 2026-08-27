skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections and clauses.
    input: >
      Path to a plain-text policy document (e.g.
      ../data/policy-documents/policy_hr_leave.txt) containing section headers
      (e.g. "2. ANNUAL LEAVE") and numbered clauses (e.g. "2.3 ...") with
      wrapped continuation lines.
    output: >
      A structured object: {source_path, header, section_order, sections},
      where sections maps each section number to {title, clauses}, and clauses
      maps each clause id (e.g. "2.3") to its full, unmodified clause text with
      wrapped lines rejoined.
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error naming
      the expected path rather than returning partial or empty structure. If a
      clause appears before any recognised section header, bucket it under an
      explicit "unsectioned" section rather than silently discarding it. Clause
      text is never rewritten or trimmed for meaning during parsing — only
      whitespace across wrapped lines is normalised.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary that preserves every clause and its full set of conditions.
    input: >
      The structured object returned by retrieve_policy (header, section_order,
      sections with clause id -> full text).
    output: >
      A plain-text summary, organised by section, listing every clause by its
      clause number with its full obligation text; clauses identified as
      multi-condition (2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are marked
      "[MULTI-CONDITION — VERBATIM]" and reproduced exactly rather than
      paraphrased. Ends with a coverage check confirming all 10 required
      clauses are present.
    error_handling: >
      If summarizing a clause risks dropping a condition, approver, or
      threshold, the skill quotes the clause verbatim and flags it instead of
      producing a shortened paraphrase. If any of the 10 required clauses is
      missing from the input structure, the summary explicitly states
      "MISSING: clause X was not found" in the coverage check rather than
      omitting it without comment. The skill never introduces text, examples,
      or framing not present in the source clauses.
