# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag based on the complaint description text.
    input: A dictionary with keys complaint_id (string/int) and description (string containing the citizen's complaint text).
    output: A dictionary with keys complaint_id, category (one of the 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing words from description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or null, return category=Other, priority=Low, reason="No description provided", flag=NEEDS_REVIEW.
      If description is ambiguous across multiple categories, pick the best match and set flag=NEEDS_REVIEW.
      Never crash on malformed input — always return a valid output row.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: input_path (string, path to a CSV file with columns complaint_id and description) and output_path (string, path where results CSV will be written).
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag — one row per input complaint.
    error_handling: >
      If the input file does not exist or is unreadable, raise a clear error with the file path.
      If a row is malformed or missing required columns, skip it and log a warning but continue processing remaining rows.
      Always produce an output file even if some rows fail — include successfully classified rows.
      Report total rows processed, succeeded, and failed at the end.
