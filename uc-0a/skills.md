skills:
  - name: classify_complaint
    description: Classifies a single complaint row to output a category, priority, reason, and flag.
    input: A single complaint row (string text).
    output: A set of fields containing category, priority, reason, and flag.
    error_handling: Sets the flag to NEEDS_REVIEW when the complaint category is genuinely ambiguous.

  - name: batch_classify
    description: Reads an input CSV containing complaints, applies classify_complaint per row, and writes an output CSV.
    input: Input CSV file path.
    output: Output CSV file path.
    error_handling: Handles missing files or bad rows gracefully by logging errors and continuing.
