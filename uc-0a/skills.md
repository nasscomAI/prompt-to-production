# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag based on description text.
    input: dict — a single CSV row with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: dict — with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is empty or missing, set category to Other, priority to Low, reason to "No description provided", flag to NEEDS_REVIEW

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes results to an output CSV file.
    input: str — file path to input CSV (e.g. test_pune.csv)
    output: str — file path to output CSV (e.g. results_pune.csv)
    error_handling: Skips malformed rows, logs a warning, and continues processing remaining rows. Produces output even if some rows fail.
