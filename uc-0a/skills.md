# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Takes a single complaint row dict and returns a classification dict with
      category, priority, reason, and flag fields according to the schema in README.md.
    input: >
      dict with keys: complaint_id (str), description (str). Example:
      {"complaint_id": "P001", "description": "Deep pothole near school entrance"}
    output: >
      dict with keys: complaint_id, category (str), priority (str),
      reason (str), flag (str or "").
    error_handling: >
      If description is missing or empty, set category: Other, priority: Standard,
      reason: "No description provided", flag: NEEDS_REVIEW.
      If description text is ambiguous, set category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads an input CSV with complaint_id and description columns, applies
      classify_complaint to every row, and writes a results CSV with all four
      output columns plus the original complaint_id.
    input: >
      input_path (str) — path to CSV with columns: complaint_id, description
    output: >
      Writes output_path (str) — CSV with columns: complaint_id, category, priority, reason, flag
    error_handling: >
      Skips rows with missing complaint_id (logs a warning). Does not crash on
      malformed rows — sets category: Other, flag: NEEDS_REVIEW for that row.
      Produces output file even if some rows fail.
