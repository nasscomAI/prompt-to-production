# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, and reason based on description text and severity keywords.
    input: Dictionary with complaint_id, description fields; other fields passed through unchanged.
    output: Dictionary with original fields plus category, priority, reason, flag columns.
    error_handling: If description is null or empty, output category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW. If description is non-text, output flag=NEEDS_REVIEW without classification attempt.

  - name: batch_classify
    description: Read input CSV file, classify each row using classify_complaint, write output CSV with results.
    input: Path to CSV file with columns complaint_id, description, and others.
    output: CSV file with input columns plus category, priority, reason, flag.
    error_handling: If input file not found, raise FileNotFoundError. If CSV is malformed, output partial results up to the error row. If a specific row fails classification, log the error and set flag=NEEDS_REVIEW for that row. Continue processing remaining rows; do not crash on single row failure.
