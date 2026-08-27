# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description text.
    input: Dictionary with keys including 'complaint_id' (string) and 'description' (string). Other fields are ignored.
    output: Dictionary with keys: complaint_id (string), category (string from allowed list), priority (string: Urgent or Standard), reason (string: one sentence citing description words), flag (string: NEEDS_REVIEW or blank).
    error_handling: >
      If description is null/empty: returns category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW.
      If no category keywords match: returns category=Other, priority=Standard (or Urgent if severity keywords present), flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes results to an output CSV file.
    input: Two file paths (string) — input_path (CSV with headers including complaint_id and description) and output_path (destination CSV).
    output: Writes CSV file with headers: complaint_id, category, priority, reason, flag. Returns None.
    error_handling: >
      Skips rows that fail to classify (logs warning, continues processing).
      Validates required columns exist before processing.
      Creates output file even if some rows are skipped.
      Raises FileNotFoundError if input file does not exist.
      Raises ValueError if required columns are missing from CSV.
