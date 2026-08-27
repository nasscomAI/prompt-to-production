# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row.
    input: A dictionary representing a single complaint row.
    output: A dictionary with keys category, priority, reason, and flag.
    error_handling: Return category 'Other' and set flag 'NEEDS_REVIEW' if input is invalid or ambiguous.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to each row, and write the output CSV.
    input: input_path (string) and output_path (string).
    output: Creates or overwrites a CSV file at output_path.
    error_handling: Must flag nulls or invalid rows, must not crash on bad rows, and must produce output even if some rows fail.
