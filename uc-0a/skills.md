skills:
  - name: classify_complaint
    description: Classify a single complaint row based on the description text.
    input: Dictionary containing a single row from the CSV (specifically the 'description' field).
    output: Dictionary with category, priority, reason, and flag.
    error_handling: Return category: 'Other', flag: 'NEEDS_REVIEW' if classification cannot be completed or the input is empty/missing.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: Path to the input test CSV file and the output CSV file.
    output: A completed CSV file with original and generated columns.
    error_handling: Skips crash on bad rows, flags null rows, and produces output even if some rows fail processing.
