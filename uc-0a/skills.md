skills:
  - name: classify_complaint
    description: Classifies one complaint row into strict UC-0A category and priority with a reason and review flag.
    input: Python dict representing one CSV row; must include complaint_id and description fields when available.
    output: Python dict with keys complaint_id, category, priority, reason, and flag.
    error_handling: Falls back to category Other and flag NEEDS_REVIEW when evidence is missing, conflicting, or row fields are malformed.

  - name: batch_classify
    description: Reads an input complaints CSV, applies classify_complaint row by row, and writes a results CSV.
    input: Input CSV path and output CSV path as strings.
    output: Output CSV file containing complaint_id, category, priority, reason, and flag columns.
    error_handling: Continues processing after row-level failures, writes fallback rows with NEEDS_REVIEW, and never aborts the full batch because of one bad row.
