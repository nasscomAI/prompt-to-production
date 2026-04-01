skills:
  - name: classify_complaint
    description: Classify a single complaint row based on its description text to determine category, priority, reason, and flag.
    input: dict with complaint_id and description text
    output: dict with complaint_id, category, priority, reason, flag
    error_handling: Return original complaint_id, category Other, priority Low, reason Error parsing input, flag NEEDS_REVIEW

  - name: batch_classify
    description: Read input CSV, classify each row using classify_complaint, and write results to output CSV.
    input: string input_path to test CSV, string output_path to write results CSV
    output: None (writes to output CSV file)
    error_handling: Log error, flag nulls, do not crash on bad rows, produce output even if some rows fail
