skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: Single complaint dictionary row including a description.
    output: Dictionary with category, priority, reason, and flag strings.
    error_handling: Return category "Other" and flag "NEEDS_REVIEW" if input is invalid or ambiguous.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint per row, and writes to an output CSV.
    input: input_path (string) and output_path (string).
    output: A completed CSV file written to the file system containing all original rows plus the classification columns.
    error_handling: Must flag nulls, not crash on bad rows, skip to next row, and produce output even if some rows fail.
