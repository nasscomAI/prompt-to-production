# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag using keyword-based rules against a fixed taxonomy.
    input: A dict representing one CSV row with keys — complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with keys — complaint_id (passthrough), category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing description keywords), flag (NEEDS_REVIEW or blank).
    error_handling: If description is null, empty, or contains no classifiable keywords, returns category "Other", priority "Low", reason "No classifiable keywords found in description", flag "NEEDS_REVIEW". Never raises an exception.

  - name: batch_classify
    description: Reads an input CSV of civic complaints, applies classify_complaint to each row, and writes a results CSV with classification output.
    input: Two strings — input_path (path to test_[city].csv) and output_path (path to write results CSV).
    output: A CSV file written to output_path with columns — complaint_id, category, priority, reason, flag. One row per input complaint.
    error_handling: If a row is malformed or causes an error, logs a warning to stderr, writes a row with flag "NEEDS_REVIEW" and reason describing the error, and continues processing remaining rows. Never crashes the batch.
