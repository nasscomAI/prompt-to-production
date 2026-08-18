skills:
  - name: classify_complaint
    description: Classify a single complaint row to category, priority, reason, and flag.
    input: Dictionary containing complaint details (specifically the complaint description).
    output: Dictionary containing category, priority, reason, and flag.
    error_handling: If description is empty or ambiguous, category is set to Other, priority is standard/low, reason states ambiguity, and flag is set to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads complaints from input CSV, applies classify_complaint per row, and writes results to output CSV.
    input: Path to the input CSV file.
    output: Path to the output CSV file.
    error_handling: Handles missing files or invalid CSV columns by raising descriptive errors and reporting status.
