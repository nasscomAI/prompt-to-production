# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A dictionary representing one CSV row with keys:
      complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: >
      A dictionary with keys:
      complaint_id (passthrough), category (one of 10 allowed values),
      priority (Urgent | Standard | Low), reason (one sentence citing description words),
      flag (NEEDS_REVIEW or blank).
    error_handling: >
      If description is empty or missing, set category to Other, priority to Low,
      reason to "No description provided", flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      input_path (str): path to the input CSV file with complaint rows.
      output_path (str): path to write the results CSV file.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority, reason, flag.
      One row per input complaint. Header row included.
    error_handling: >
      If a row fails classification, log the error, set all fields to empty except
      complaint_id, set flag to NEEDS_REVIEW, and continue processing the remaining rows.
      Never crash on a single bad row.
