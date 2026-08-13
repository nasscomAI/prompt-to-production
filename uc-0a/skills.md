# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: dict of one complaint row (keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open)
    output: dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If the description matches no allowed category, return category: Other and flag: NEEDS_REVIEW. If the description is empty or the row is malformed, return category: Other and flag: NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: Read an input CSV, classify every row, and write a results CSV.
    input: input_path (path to test_[city].csv) and output_path (path to write results CSV)
    output: CSV file with columns: complaint_id, category, priority, reason, flag
    error_handling: Skip null or malformed rows but keep the output file complete; classify every valid row; never crash the run on a single bad row.
