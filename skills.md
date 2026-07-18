# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a plain-text policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: Structured list of numbered sections, each containing clause number, heading (if any), and full clause text preserved verbatim.
    error_handling: >
      If the file path is invalid, the file is empty, or the content is not a
      recognizable structured policy document (no numbered clauses detected),
      return an error message and refuse to proceed. Never fabricate or infer
      missing content.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: Structured numbered sections (output of retrieve_policy) — a list of clause objects with clause number and full text.
    output: >
      A summary where each numbered clause from the source is represented with
      its clause reference (e.g., 2.3, 5.2), binding verbs preserved exactly
      (must, will, requires, not permitted), and all conditions within
      multi-condition obligations retained. Clauses that cannot be summarised
      without meaning loss are quoted verbatim and flagged with
      [VERBATIM — meaning loss risk].
    error_handling: >
      If input sections are empty or malformed, return an error and refuse to
      summarize. If a clause contains ambiguous or contradictory obligations,
      quote it verbatim and flag it rather than interpreting. Never add
      information not present in the source. Never soften binding verbs.
