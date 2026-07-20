# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A dictionary representing one complaint row with keys: complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
    output: >
      A dictionary with keys: complaint_id, category (one of the 10 allowed values),
      priority (Urgent/Standard/Low), reason (one sentence citing words from description),
      flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or null, return category=Other, priority=Low,
      reason="No description provided", flag=NEEDS_REVIEW. Never crash on bad input.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to an output CSV.
    input: >
      Input CSV file path (with columns: complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open) and output CSV file path.
    output: >
      A CSV file at the output path with columns: complaint_id, category, priority,
      reason, flag. One row per input complaint.
    error_handling: >
      If the input file does not exist or has missing columns, print an error and exit.
      If individual rows fail classification, log the error and continue processing
      remaining rows — never halt the entire batch for one bad row.
