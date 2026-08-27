skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: Dictionary containing complaint_id and complaint text
    output: Dictionary with complaint_id, category, priority, reason, and flag
    error_handling: If text is empty or unclear, return category "Other" and flag "NEEDS_REVIEW"

  - name: batch_classify
    description: Reads input CSV, applies classification to each row, and writes output CSV.
    input: Input CSV file path
    output: Output CSV file with classification results
    error_handling: Skips invalid rows and continues processing without crashing