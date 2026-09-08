skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and review flag.
    input: A dictionary representing one CSV row with keys including complaint_id and description (string).
    output: A dictionary with keys complaint_id (string), category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (string citing keywords), flag (NEEDS_REVIEW or empty string).
    error_handling: If description is missing, empty, or non-string, return category Other, priority Standard, reason "No description provided", flag NEEDS_REVIEW. Never crash on malformed input.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: Two file paths — input_csv (path to CSV with complaint rows) and output_csv (path to write classified results).
    output: A CSV file at output_csv with columns complaint_id, category, priority, reason, flag — one row per input complaint.
    error_handling: Skip malformed or unreadable rows, log the error to stdout, and continue processing remaining rows. Produce output file even if some rows fail.
