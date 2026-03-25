skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: Dictionary containing a single complaint row.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Handle missing descriptions by returning Other and marking flag as NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the output to a CSV.
    input: String path to input CSV file and output CSV file.
    output: Writes results to output CSV file path.
    error_handling: Flag nulls, do not crash on bad rows, and produce output even if some rows fail.
