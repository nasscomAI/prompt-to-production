skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: Dictionary containing complaint details including the description.
    output: Dictionary with added keys category, priority, reason, and flag.
    error_handling: Sets flag to NEEDS_REVIEW when ambiguous and defaults to Other category.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths to input CSV and output CSV.
    output: CSV file containing the original columns plus category, priority, reason, and flag.
    error_handling: Flags nulls, does not crash on bad rows, and produces an output file even if some rows fail.
