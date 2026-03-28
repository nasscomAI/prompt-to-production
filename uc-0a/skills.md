# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: >
      A dict representing one CSV row with keys: complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open.
    output: >
      A dict with keys: complaint_id, category (one of the 10 allowed values),
      priority (Urgent, Standard, or Low), reason (one sentence citing words from
      the description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If the description is empty or missing, set category to Other, priority to Low,
      reason to "No description provided", and flag to NEEDS_REVIEW. If the description
      is ambiguous and does not clearly match any category, set category to Other and
      flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes a results CSV.
    input: >
      input_path (str): path to the city test CSV file.
      output_path (str): path for the results CSV file.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag — one row per input complaint, in the same order as the input.
    error_handling: >
      If the input file is missing or unreadable, exit with a clear error message.
      If any row fails classification, log the complaint_id and continue processing
      remaining rows rather than aborting the entire batch.
