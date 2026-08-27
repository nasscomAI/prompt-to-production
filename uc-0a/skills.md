skills:
  - name: classify_complaint
    description: Classify a single complaint row into standard category, priority, citation reason, and review flag.
    input: Dictionary representing a single CSV row with keys like complaint_id, description, etc.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: If input is malformed or ambiguous, uses category 'Other' and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to each row, and write output CSV.
    input: Absolute file paths to input CSV and output CSV.
    output: Writes output CSV containing columns complaint_id, category, priority, reason, flag.
    error_handling: Flags nulls, logs parsing errors, does not crash on bad rows, and produces output even if some rows fail.
