# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into the fixed UC-0A taxonomy, returning
      category, priority, a justification quoting the description, and an
      ambiguity flag. Stateless and independent per row.
    input: >
      dict with at minimum:
        complaint_id: str   (non-empty identifier passed through unchanged)
        description:  str   (free-text citizen complaint)
      Extra columns from the source CSV are ignored, not used for classification.
    output: >
      dict with exactly these keys:
        complaint_id: str
        category:     str   (one of the 10 allowed values from README.md)
        priority:     str   (Urgent | Standard | Low)
        reason:       str   (one sentence; must contain a substring of description)
        flag:         str   (NEEDS_REVIEW or "")
    error_handling: >
      - Empty / null / <5-char description -> category=Other, priority=Standard,
        flag=NEEDS_REVIEW, reason="description missing or too short to classify".
      - Description does not match any specific category -> category=Other,
        flag=NEEDS_REVIEW, reason quotes the ambiguous phrase.
      - Severity keyword present but category unclear -> still Urgent, category=Other,
        flag=NEEDS_REVIEW. Severity is never downgraded to satisfy schema.
      - Never raises on bad input; always returns a schema-valid row.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to each row,
      and write a results CSV. Resilient: a single bad row never aborts the run.
    input: >
      input_path:  str  (path to test_[city].csv with columns including
                         complaint_id and description)
      output_path: str  (path to write results CSV)
    output: >
      Writes a CSV at output_path with header:
        complaint_id, category, priority, reason, flag
      One row per input row, in the same order. Returns None.
      Prints a summary line: total rows, NEEDS_REVIEW count, error count.
    error_handling: >
      - Missing input file -> raise FileNotFoundError before opening output.
      - Row missing complaint_id -> skip row, increment error count, log to stderr.
      - Row missing description column -> treat description as empty (delegated to
        classify_complaint, which will flag NEEDS_REVIEW).
      - Exception inside classify_complaint for one row -> write a fallback row
        (category=Other, priority=Standard, flag=NEEDS_REVIEW,
        reason="classifier error: <exception class>") and continue.
      - Output is always written, even if every row failed, so partial results
        are inspectable.
