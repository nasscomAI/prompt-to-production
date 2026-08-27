# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A dictionary representing one CSV row with keys: complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
    output: >
      A dictionary with keys: complaint_id (from input), category (one of the 10
      allowed values), priority (Urgent/Standard/Low), reason (one sentence citing
      specific words from description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or null, return category=Other, priority=Standard,
      reason="No description provided", flag=NEEDS_REVIEW.
      If description matches multiple categories equally, pick best fit and set
      flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies each row using classify_complaint, and writes the results to an output CSV.
    input: >
      Two file paths: input_path (path to test_[city].csv) and output_path
      (path to write results_[city].csv).
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag. One row per input complaint. Returns count of processed and
      failed rows to stdout.
    error_handling: >
      If a row fails classification (malformed data, missing fields), log the
      error with the complaint_id, skip the row, and continue processing.
      The output CSV must still be produced even if some rows fail.
      Report total rows processed, succeeded, and failed at the end.
