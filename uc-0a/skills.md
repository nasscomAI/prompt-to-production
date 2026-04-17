skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row based on RICE enforcement rules.
    input: Dictionary containing complaint details (complaint_id, description, etc.).
    output: Dictionary containing category, priority, reason, and flag fields.
    error_handling: Return NEEDS_REVIEW flag and "Other" category if input description is ambiguous or matches multiple categories.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: Filepath string for input CSV, filepath string for output CSV.
    output: Writes an output CSV file with results.
    error_handling: Skip invalid rows and log errors, but continue processing the rest of the batch without crashing.
