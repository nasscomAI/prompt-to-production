# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into category, priority,
      reason, and flag based on the enforcement rules in agents.md.
    input: >
      A dictionary representing one CSV row with keys: complaint_id,
      date_raised, city, ward, location, description, reported_by,
      days_open.
    output: >
      A dictionary with keys: complaint_id (preserved from input),
      category (one of 10 allowed values), priority (Urgent/Standard/Low),
      reason (single sentence citing words from description),
      flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing or empty, return category=Other,
      priority=Low, reason="No description provided", flag=NEEDS_REVIEW.
      If description does not match any specific category, return
      category=Other with flag=NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV of citizen complaints, apply classify_complaint
      to each row, and write the results to an output CSV.
    input: >
      Two file paths: input_path (path to test_[city].csv) and
      output_path (path to write results_[city].csv).
    output: >
      A CSV file at output_path with columns: complaint_id, category,
      priority, reason, flag — one row per input complaint.
    error_handling: >
      If a row fails classification, write it to the output with
      category=Other, priority=Low, reason="Classification error",
      flag=NEEDS_REVIEW. Never crash — always produce an output file
      even if some rows fail. Print a summary of total rows processed
      and any rows that needed error fallback.
