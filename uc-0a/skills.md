# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into the official category, priority, and flag, with a reason that justifies the choice.
    input: dict — one CSV row with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: dict — keys: complaint_id, category (one of the ten exact taxonomy strings), priority (Urgent | Standard | Low), reason (one sentence quoting specific words from the description), flag (NEEDS_REVIEW or empty string).
    error_handling: Empty or missing description → category: Other, priority: Standard, flag: NEEDS_REVIEW. Ambiguous description → category: Other, flag: NEEDS_REVIEW. Never crashes and always returns all five required keys.

  - name: batch_classify
    description: Applies classify_complaint to every row of an input CSV and writes the classified results to an output CSV.
    input: input_path (str) — path to a test_[city].csv file; output_path (str) — path where the results CSV will be written.
    output: CSV file at output_path with one row per input row containing complaint_id, category, priority, reason, flag. Prints a confirmation with the output path.
    error_handling: Bad or missing rows are flagged, never fatal — every valid row still produces output. Blank descriptions are classified as Other + NEEDS_REVIEW. Results are written even if some rows fail.
