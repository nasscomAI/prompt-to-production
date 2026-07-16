skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into category, priority, reason, and flag
      using strict enforcement rules.
    input: >
      dict — keys: complaint_id (str), description (str)
    output: >
      dict — keys: complaint_id, category, priority, reason, flag
    error_handling: >
      If description is empty, set category: Other, priority: Low, reason: "No description provided", flag: NEEDS_REVIEW.
      If category is ambiguous, set category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, classify every row, and write the
      results CSV. Continues on per-row errors and never crashes on bad input.
    input: >
      input_path (str) — path to CSV with complaint_id and description columns
    output: >
      output_path (str) — writes CSV with columns: complaint_id, category, priority, reason, flag
    error_handling: >
      Rows with missing complaint_id or description are written with category: Other,
      priority: Low, reason: "Invalid row", flag: NEEDS_REVIEW. Processing always
      continues to the next row. Writes partial results even if some rows fail.
