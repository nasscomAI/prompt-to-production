# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into the fixed schema — category, priority, reason, flag — from the description text alone.
    input: One complaint row (dict) — complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: dict with keys complaint_id, category (one of the 10 allowed strings), priority (Urgent / Standard / Low), reason (one sentence quoting description words), flag (NEEDS_REVIEW or blank)
    error_handling: If the category cannot be determined from the description alone, returns category: Other with flag: NEEDS_REVIEW instead of guessing. Never emits categories outside the allowed list.

  - name: batch_classify
    description: Reads the input complaint CSV, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (string, path to test_[city].csv), output_path (string, path to write results_[city].csv)
    output: CSV file with header and one row per complaint — complaint_id, category, priority, reason, flag — written even if some rows fail
    error_handling: Never crashes on a bad row — flags or skips the row and continues so the output is produced. Reports the number of rows classified and any rows that could not be processed.
