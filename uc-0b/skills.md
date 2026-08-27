# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into a list of numbered sections, each tagged with its clause number and raw text.
    input: >
      A file path string pointing to a .txt policy document (e.g.
      policy_hr_leave.txt). No other sources are loaded or consulted.
    output: >
      A list of dicts, one per detected clause, each with:
        clause_id   — string, e.g. "2.3", "5.2"
        heading     — string, the clause title if present, else empty string
        body        — string, the full raw text of that clause
      Plus a top-level metadata dict:
        { file_path: str, total_clauses: int, raw_text: str }
    error_handling: >
      If the file does not exist, print a clear error and exit without
      producing output. If the file is empty or contains no detectable
      numbered clauses, return the raw_text with total_clauses: 0 and
      emit a warning — do not silently proceed with an empty clause list.

  - name: summarize_policy
    description: Takes the structured clause list from retrieve_policy and produces a compliant summary where every clause is present, all conditions are preserved, and no external information is introduced.
    input: >
      The output of retrieve_policy: a list of clause dicts
      ({ clause_id, heading, body }) and the metadata dict.
    output: >
      A plain-text summary file where:
        - Every clause is represented under its clause number (e.g. "2.3 — ...")
        - Multi-condition obligations list ALL conditions explicitly
        - Each entry ends with its source clause_id in brackets, e.g. [clause 5.2]
        - Any clause that cannot be paraphrased without meaning loss is quoted
          verbatim and appended with the marker: [VERBATIM_REQUIRED]
        - No sentence contains: "typically", "generally", "as is standard practice",
          "as in most organisations", or any phrase not grounded in the source text
    error_handling: >
      If a required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)
      is absent from the input clause list, append a warning line:
      "WARNING: Clause [X] not found in source document — summary may be incomplete."
      Never silently omit a clause; never invent content to fill a missing clause.
