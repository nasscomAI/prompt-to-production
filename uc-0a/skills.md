# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag based on the description text.
    input: >
      A dictionary (single CSV row) with keys: complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open. Only the "description"
      field is used for classification.
    output: >
      A dictionary with keys: complaint_id (pass-through from input),
      category (one of 10 allowed values), priority (Urgent | Standard | Low),
      reason (single sentence citing words from description),
      flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty, None, or whitespace-only, return category=Other,
      priority=Low, reason="Description missing or unintelligible",
      flag=NEEDS_REVIEW. If any unexpected error occurs during classification,
      return the same fallback output rather than crashing.

  - name: batch_classify
    description: Read an input CSV of complaints, classify each row using classify_complaint, and write results to an output CSV.
    input: >
      Two file paths — input_path (path to test_[city].csv with columns:
      complaint_id, date_raised, city, ward, location, description, reported_by,
      days_open) and output_path (path to write the results CSV).
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag. One row per input complaint. The file is written even if
      some rows fail classification (those rows get fallback values).
    error_handling: >
      If input file does not exist or is unreadable, raise FileNotFoundError
      with a clear message. If a single row fails classification, log a warning,
      write the fallback output for that row, and continue processing remaining
      rows. Never crash mid-batch — always produce an output file.
