# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and review flag.
    input: A dictionary (single CSV row) with keys — complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dictionary with keys — complaint_id, category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing or empty, returns category=Other, priority=Low, reason="No description provided", flag=NEEDS_REVIEW. Never crashes on malformed input.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to an output CSV.
    input: Two file paths — input_path (path to test_[city].csv) and output_path (path to write results_[city].csv).
    output: A CSV file at output_path with columns — complaint_id, category, priority, reason, flag. One row per input complaint.
    error_handling: Skips rows that cause errors (logs warning to stderr), continues processing remaining rows, and writes partial output. Flags null/empty description rows with NEEDS_REVIEW. Never crashes on bad rows.
