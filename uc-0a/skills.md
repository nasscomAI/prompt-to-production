# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using deterministic keyword matching against the allowed schema.
    input: A dict representing one CSV row with keys complaint_id and description.
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: Returns category Other and flag NEEDS_REVIEW if description is blank or no category keyword matches; handles missing keys gracefully.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results to an output CSV.
    input: Input CSV file path and output CSV file path.
    output: Writes a results CSV with columns complaint_id, category, priority, reason, flag.
    error_handling: Skips rows that cannot be parsed, logs a warning, and still produces a valid output CSV even if some rows fail.