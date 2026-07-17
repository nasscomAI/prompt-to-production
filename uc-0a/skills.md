# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and review flag based on the description text.
    input: >
      A dictionary representing one CSV row with keys: complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
    output: >
      A dictionary with keys:
      - complaint_id (string): preserved from input
      - category (string): one of the 10 allowed values
      - priority (string): Urgent, Standard, or Low
      - reason (string): one sentence citing specific description words
      - flag (string): NEEDS_REVIEW or empty string
    error_handling: >
      If the description field is empty, null, or missing, return category=Other,
      priority=Low, reason="Description is empty or unintelligible",
      flag=NEEDS_REVIEW. Never crash on bad input — always produce a row.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes a results CSV with classification output.
    input: >
      Two file paths (strings): input_path pointing to the test CSV file,
      output_path for writing the results CSV.
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag. One row per input complaint. Console output reports total
      rows processed, how many flagged NEEDS_REVIEW, and how many marked Urgent.
    error_handling: >
      If input file does not exist or is unreadable, print an error and exit.
      If a single row fails to classify, write it with category=Other,
      priority=Low, flag=NEEDS_REVIEW and continue processing remaining rows.
      Never crash mid-batch — always produce partial output.
