skills:
  - name: classify_complaint
    description: Classify a single complaint row.
    input: dict with keys: complaint_id, category, priority, reason, flag
    output: dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW

  - name: batch_classify
    description: Batch classify complaints from a CSV file.
    input: Path to input CSV file
    output: Path to output CSV file
    error_handling: If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW
