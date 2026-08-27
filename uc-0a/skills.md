skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag according to the schema.
    input: A dictionary with at minimum a 'description' key containing the complaint text string.
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or missing, return category 'Other', priority 'Standard', reason 'Empty description', flag 'NEEDS_REVIEW'. If severity keywords are present but description is ambiguous, still assign Urgent priority and flag appropriately.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes the results CSV with all required columns.
    input: Path to input CSV (string), path to output CSV (string). CSV must have at minimum complaint_id and description columns.
    output: Writes a CSV file at the specified output path with columns: complaint_id, category, priority, reason, flag.
    error_handling: Skips malformed rows with a warning, never crashes on bad data, always produces output for valid rows. Reports total rows processed, skipped, and written.
