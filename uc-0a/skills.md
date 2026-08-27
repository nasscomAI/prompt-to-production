# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag based on the complaint description text.
    input: A dictionary representing one complaint row with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dictionary with keys: complaint_id, category (one of 10 allowed strings), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing or empty, set category to Other, flag to NEEDS_REVIEW, and reason to "Description not provided." If complaint_id is missing, generate a placeholder ID and flag for review.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the classified results to an output CSV file.
    input: Two file paths — input_path (CSV with columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open) and output_path (destination CSV path).
    output: A CSV file at output_path with columns: complaint_id, category, priority, reason, flag. One output row per input row.
    error_handling: If input file does not exist or is unreadable, raise FileNotFoundError with descriptive message. If individual rows fail classification, include them in output with category=Other, flag=NEEDS_REVIEW, and reason citing the error. Never skip rows — produce output for every input row.
