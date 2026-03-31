# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: dict with keys: complaint_id, description, days_open, reported_by, ward, location
    output: dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is missing or empty, return category=Other, priority=Low, flag=NEEDS_REVIEW. If days_open is missing or non-numeric, treat as 0.

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies each row, and writes results to an output CSV.
    input: input_path (str, path to CSV), output_path (str, path to write results CSV)
    output: CSV file at output_path with columns: complaint_id, category, priority, reason, flag
    error_handling: Skip rows with missing complaint_id. Log and continue on per-row classification failure — do not crash the batch. Write partial output if some rows fail.
