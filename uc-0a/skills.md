skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag.
    input: A dict with at minimum complaint_id (str) and description (str). May include other metadata fields.
    output: A dict with keys complaint_id, category, priority, reason, flag — all values are strings.
    error_handling: If input is missing complaint_id or description, raise ValueError. If description is empty, set category to Other, flag to NEEDS_REVIEW, reason to "Empty description provided." If category is genuinely ambiguous, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV, classify every row using classify_complaint, and write results to an output CSV.
    input: input_path (str) — path to CSV file with at minimum complaint_id and description columns. output_path (str) — path to write results CSV.
    output: None. Writes a CSV with columns: complaint_id, category, priority, reason, flag.
    error_handling: If input file does not exist, raise FileNotFoundError. If a row is missing required columns, skip it and continue processing other rows. Always produce output even if some rows fail. Never crash on bad rows.
