skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dict with complaint_id and description keys.
    output: A dict with complaint_id, category, priority, reason, and flag keys.
    error_handling: If description is missing or empty, sets category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, classifies each row, and writes results CSV.
    input: Path to input CSV file and path to output CSV file.
    output: Writes a CSV file with columns: complaint_id, category, priority, reason, flag.
    error_handling: Skips malformed rows with a warning, continues processing remaining rows. Always produces output even if some rows fail.
