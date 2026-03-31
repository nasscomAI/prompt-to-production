skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: Dictionary representing a single row of a complaint with at least a description field.
    output: Dictionary with keys category, priority, reason, flag.
    error_handling: When input is ambiguous or matches a failure mode, flag is set to NEEDS_REVIEW and category to Other.

  - name: batch_classify
    description: Read input CSV, classify each row, write results CSV.
    input: File paths for input CSV and output CSV.
    output: Outputs a CSV file to disk.
    error_handling: Flags nulls, does not crash on bad rows, produces output even if some rows fail.
