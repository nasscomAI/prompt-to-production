
skills:
  - name: classify_complaint
    description: Classify a single complaint record into category, priority, reason, and review flag.
    input: dict with complaint fields including complaint_id and description.
    output: dict with keys complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or the complaint is ambiguous, return category Other, priority Standard, a clear reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to every row, and write the results to an output CSV.
    input: input_path string and output_path string.
    output: CSV file containing complaint_id, category, priority, reason, and flag for each row.
    error_handling: Continues processing all rows even if some are invalid; invalid rows are written with category Other and flag NEEDS_REVIEW.
